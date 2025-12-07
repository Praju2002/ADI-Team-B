"""
Helpers to compute Non-Revenue Water (NRW) using a volumetric-first strategy.

Functions here prefer volumetric (m3) calculations using production and
service/consumption tables when available, and fall back to financial
calculations (billed/paid) if volumetric data is not present.
"""
from typing import Optional, Dict, Any
import pandas as pd


def _ensure_date_col(df: pd.DataFrame, colname: str = 'date') -> pd.DataFrame:
    if colname in df.columns:
        df = df.copy()
        df[colname] = pd.to_datetime(df[colname], errors='coerce')
        df['year_month'] = df[colname].dt.to_period('M').astype(str)
    else:
        df = df.copy()
        df['year_month'] = None
    return df


def compute_volumetric_nrw(production_df: pd.DataFrame, w_service_df: pd.DataFrame, country: Optional[str] = None) -> Dict[str, Any]:
    """Compute NRW in m3 using production (system input) and w_service consumption.

    Returns dict with keys: mode='volumetric', national (df), zone (df), top_zones (df).
    """
    # Basic checks
    if production_df is None or w_service_df is None or production_df.empty or w_service_df.empty:
        return {'mode': 'none'}

    prod = production_df.copy()
    ws = w_service_df.copy()

    prod = _ensure_date_col(prod, 'date')
    ws = _ensure_date_col(ws, 'date')

    # Identify production and consumption column names
    prod_col = None
    for c in ['production_m3', 'production', 'production_m_3']:
        if c in prod.columns:
            prod_col = c
            break

    cons_col = None
    for c in ['total_consumption', 'consumption_m3', 'consumption']:
        if c in ws.columns:
            cons_col = c
            break

    if prod_col is None or cons_col is None:
        return {'mode': 'none'}

    # Aggregate production to month (national)
    prod_month = prod.groupby('year_month', as_index=False)[prod_col].sum().rename(columns={prod_col: 'system_input_m3'})

    # Aggregate consumption by zone-month and national
    zone_col = 'zone' if 'zone' in ws.columns else ('city' if 'city' in ws.columns else None)
    if zone_col:
        cons_zone_month = ws.groupby([zone_col, 'year_month'], as_index=False)[cons_col].sum().rename(columns={cons_col: 'consumption_m3'})
    else:
        cons_zone_month = ws.groupby(['year_month'], as_index=False)[cons_col].sum().rename(columns={cons_col: 'consumption_m3'})

    cons_national = cons_zone_month.groupby('year_month', as_index=False)['consumption_m3'].sum()

    # Merge and compute
    bal = prod_month.merge(cons_national, on='year_month', how='outer').sort_values('year_month')
    bal['system_input_m3'] = bal['system_input_m3'].fillna(0)
    bal['consumption_m3'] = bal['consumption_m3'].fillna(0)
    bal['nrw_m3'] = bal['system_input_m3'] - bal['consumption_m3']
    bal['nrw_pct_of_input'] = bal.apply(lambda r: (r['nrw_m3'] / r['system_input_m3'] * 100) if r['system_input_m3'] > 0 else float('nan'), axis=1)

    # Top zones by consumption in the latest 12 months if zone available
    last12 = sorted(cons_zone_month['year_month'].unique())[-12:]
    recent = cons_zone_month[cons_zone_month['year_month'].isin(last12)] if not cons_zone_month.empty else cons_zone_month
    if not recent.empty and zone_col:
        top = recent.groupby(zone_col, as_index=False)['consumption_m3'].sum().sort_values('consumption_m3', ascending=False)
        top10 = top.head(10)
    else:
        top10 = pd.DataFrame(columns=[zone_col or 'zone', 'consumption_m3'])

    return {
        'mode': 'volumetric',
        'national': bal,
        'zone': cons_zone_month,
        'top_zones': top10,
        'zone_col': zone_col
    }


def compute_financial_nrw(billing_df: pd.DataFrame, country: Optional[str] = None) -> Dict[str, Any]:
    """Compute NRW using billed/paid money fields (fallback).

    Returns dict with keys: mode='financial', national (df), zone (df) similar structure.
    """
    if billing_df is None or billing_df.empty:
        return {'mode': 'none'}

    b = billing_df.copy()
    b = _ensure_date_col(b, 'date')

    if 'billed' not in b.columns or 'paid' not in b.columns:
        return {'mode': 'none'}

    # zone fallback
    if 'zone' not in b.columns:
        if 'city' in b.columns:
            b['zone'] = b['city']
        elif 'country' in b.columns:
            b['zone'] = b['country']
        else:
            b['zone'] = 'All Zones'

    b['billed'] = pd.to_numeric(b['billed'], errors='coerce').fillna(0)
    b['paid'] = pd.to_numeric(b['paid'], errors='coerce').fillna(0)
    b['year_month'] = b['date'].dt.to_period('M').astype(str)

    nrw_zone = b.groupby(['zone', 'year_month'], as_index=False).agg({'billed': 'sum', 'paid': 'sum'})
    nrw_zone['nrw_amount'] = nrw_zone['billed'] - nrw_zone['paid']
    nrw_zone['nrw_rate'] = nrw_zone.apply(lambda r: (r['nrw_amount'] / r['billed'] * 100) if r['billed'] > 0 else float('nan'), axis=1)

    nrw_national = nrw_zone.groupby('year_month', as_index=False).agg({'billed': 'sum', 'paid': 'sum'})
    nrw_national['nrw_amount'] = nrw_national['billed'] - nrw_national['paid']
    nrw_national['nrw_rate'] = nrw_national.apply(lambda r: (r['nrw_amount'] / r['billed'] * 100) if r['billed'] > 0 else float('nan'), axis=1)

    return {
        'mode': 'financial',
        'national': nrw_national,
        'zone': nrw_zone,
        'top_zones': nrw_zone.groupby('zone', as_index=False)['nrw_amount'].sum().sort_values('nrw_amount', ascending=False).head(10),
        'zone_col': 'zone'
    }


def compute_best_nrw(billing_df: pd.DataFrame, production_df: pd.DataFrame, w_service_df: pd.DataFrame, country: Optional[str] = None) -> Dict[str, Any]:
    """Try volumetric first, fallback to financial if needed."""
    vol = compute_volumetric_nrw(production_df, w_service_df, country)
    if vol.get('mode') == 'volumetric':
        # If volumetric totals are reasonable (not all zero) return
        national = vol.get('national')
        if national is not None and national['system_input_m3'].sum() > 0:
            return vol

    # Fallback
    fin = compute_financial_nrw(billing_df, country)
    if fin.get('mode') == 'financial':
        return fin

    return {'mode': 'none'}
