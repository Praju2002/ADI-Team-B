"""
Centralized data loading module with caching for optimal performance
"""
import streamlit as st
import pandas as pd
import os
from pathlib import Path
import glob
import time

# Optional dependency: pyarrow is required for parquet. If missing, we'll still work but parquet caching will be disabled.
try:
    import pyarrow  # noqa: F401
    _HAS_PARQUET = True
except Exception:
    _HAS_PARQUET = False


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_from_csv():
    """Load data from individual CSV files"""
    data = {}
    countries = ['cameroon', 'lesotho', 'malawi', 'uganda']
    base_path = Path('Raw_Data')
    
    # Initialize empty dataframes
    all_fin_service_list = []
    all_national_list = []
    billing_list = []
    production_list = []
    s_access_list = []
    s_service_list = []
    w_access_list = []
    w_service_list = []
    
    for country in countries:
        country_path = base_path / country
        try:
            # Load each file type
            if (country_path / f'all_fin_service_{country}.csv').exists():
                df = pd.read_csv(country_path / f'all_fin_service_{country}.csv')
                df['country'] = country.capitalize()
                all_fin_service_list.append(df)
            
            if (country_path / f'all_nationalacc_{country}.csv').exists():
                df = pd.read_csv(country_path / f'all_nationalacc_{country}.csv')
                df['country'] = country.capitalize()
                all_national_list.append(df)
            
            if (country_path / f'billing_{country}.csv').exists():
                billing_file = country_path / f'billing_{country}.csv'
                try:
                    # Read header first to pick only needed columns and set dtypes
                    header = pd.read_csv(billing_file, nrows=0).columns.tolist()
                    desired = ['date', 'country', 'billed', 'water_billed', 'sewer_billed']
                    usecols = [c for c in desired if c in header]
                    dtypes = {}
                    if 'country' in header:
                        dtypes['country'] = 'string'
                    for col in ['billed', 'water_billed', 'sewer_billed']:
                        if col in header:
                            dtypes[col] = 'float64'

                    parse_dates = ['date'] if 'date' in usecols else None
                    df = pd.read_csv(billing_file, usecols=usecols, dtype=dtypes, parse_dates=parse_dates, low_memory=False)

                    # Ensure country column exists and is normalized
                    if 'country' not in df.columns:
                        df['country'] = country.capitalize()
                    else:
                        try:
                            df['country'] = df['country'].astype(str).str.strip().str.capitalize()
                        except Exception:
                            df['country'] = country.capitalize()

                    billing_list.append(df)
                except Exception:
                    # Fallback to full read if anything fails
                    df = pd.read_csv(billing_file, low_memory=False)
                    df['country'] = country.capitalize()
                    billing_list.append(df)
            
            if (country_path / f'production_{country}.csv').exists():
                df = pd.read_csv(country_path / f'production_{country}.csv')
                df['country'] = country.capitalize()
                production_list.append(df)
            
            if (country_path / f's_access_{country}.csv').exists():
                df = pd.read_csv(country_path / f's_access_{country}.csv')
                df['country'] = country.capitalize()
                s_access_list.append(df)
            
            if (country_path / f's_service_{country}.csv').exists():
                df = pd.read_csv(country_path / f's_service_{country}.csv')
                df['country'] = country.capitalize()
                s_service_list.append(df)
            
            if (country_path / f'w_access_{country}.csv').exists():
                df = pd.read_csv(country_path / f'w_access_{country}.csv')
                df['country'] = country.capitalize()
                w_access_list.append(df)
            
            if (country_path / f'w_service_{country}.csv').exists():
                df = pd.read_csv(country_path / f'w_service_{country}.csv')
                df['country'] = country.capitalize()
                w_service_list.append(df)
        except Exception as e:
            st.warning(f"Error loading data for {country}: {e}")
    
    # Concatenate all dataframes
    data['all_fin_service'] = pd.concat(all_fin_service_list, ignore_index=True) if all_fin_service_list else pd.DataFrame()
    data['all_national'] = pd.concat(all_national_list, ignore_index=True) if all_national_list else pd.DataFrame()
    data['billing'] = pd.concat(billing_list, ignore_index=True) if billing_list else pd.DataFrame()
    data['production'] = pd.concat(production_list, ignore_index=True) if production_list else pd.DataFrame()
    data['s_access'] = pd.concat(s_access_list, ignore_index=True) if s_access_list else pd.DataFrame()
    data['s_service'] = pd.concat(s_service_list, ignore_index=True) if s_service_list else pd.DataFrame()
    data['w_access'] = pd.concat(w_access_list, ignore_index=True) if w_access_list else pd.DataFrame()
    data['w_service'] = pd.concat(w_service_list, ignore_index=True) if w_service_list else pd.DataFrame()
    
    return data


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_all_data():
    """Load all data with caching - Single source of truth"""
    try:
        processed_dir = Path('Raw_Data/processed')

        def processed_is_fresh():
            """Return True if the processed parquet directory exists and is newer than any source files."""
            if not _HAS_PARQUET:
                return False
            if not processed_dir.exists():
                return False
            marker = processed_dir / 'processed.timestamp'
            if marker.exists():
                try:
                    processed_mtime = float(marker.read_text())
                except Exception:
                    processed_mtime = processed_dir.stat().st_mtime
            else:
                processed_mtime = processed_dir.stat().st_mtime

            # Compare against all CSV/XLSX in Raw_Data
            src_files = glob.glob('Raw_Data/**/*.csv', recursive=True) + glob.glob('Raw_Data/**/*.xlsx', recursive=True)
            for f in src_files:
                try:
                    if os.path.getmtime(f) > processed_mtime:
                        return False
                except OSError:
                    return False
            return True

        # If processed parquet exists and is fresh, load and return it
        if processed_is_fresh():
            try:
                with st.spinner('Loading preprocessed parquet data...'):
                    data = {}
                    for p in processed_dir.glob('*.parquet'):
                        key = p.stem
                        try:
                            data[key] = pd.read_parquet(p)
                        except Exception:
                            data[key] = pd.DataFrame()
                    # Ensure all expected keys exist
                    for k in ['all_fin_service','all_national','billing','production','s_access','s_service','w_access','w_service']:
                        if k not in data:
                            data[k] = pd.DataFrame()
                    return data
            except Exception:
                # If reading parquet fails, fall through to normal load
                pass
        # Try loading from Excel first
        if os.path.exists('Raw_Data/Master_Data.xlsx'):
            # Load sheets into a dict first, then normalize
            data = {
                'all_fin_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='all_fin_service'),
                'all_national': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='all_national'),
                'billing': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='billing'),
                'production': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='production'),
                's_access': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='s_access'),
                's_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='s_service'),
                'w_access': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='w_access'),
                'w_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='w_service')
            }

            # Normalize country casing and parse date-like columns across all dataframes
            for key, df in data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # Normalize country column to Capitalized form (e.g., 'Cameroon')
                    if 'country' in df.columns:
                        try:
                            df['country'] = df['country'].astype(str).str.strip().str.capitalize()
                        except Exception:
                            pass

                    # Parse any date-like columns (columns containing 'date') to datetime
                    date_cols = [c for c in df.columns if 'date' in str(c).lower()]
                    for c in date_cols:
                        try:
                            df[c] = pd.to_datetime(df[c], errors='coerce')
                        except Exception:
                            pass

            # If Excel was present but all sheets are empty, fall back to CSV loading
            try:
                all_empty = all(isinstance(df, pd.DataFrame) and df.empty for df in data.values())
            except Exception:
                all_empty = False
            if all_empty:
                # Force fall-through to CSV loading
                raise FileNotFoundError("Excel file present but sheets empty; falling back to CSV files")

            # After loading & normalizing from Excel, attempt to save per-table parquet files for faster subsequent loads
            try:
                if _HAS_PARQUET:
                    processed_dir = Path('Raw_Data/processed')
                    processed_dir.mkdir(parents=True, exist_ok=True)
                    for key, df in data.items():
                        try:
                            if isinstance(df, pd.DataFrame):
                                # write table even if empty to make cache deterministic
                                df.to_parquet(processed_dir / f"{key}.parquet", index=False)
                        except Exception:
                            pass
                    with open(processed_dir / 'processed.timestamp', 'w') as fh:
                        fh.write(str(time.time()))
            except Exception:
                pass

            return data
        else:
            raise FileNotFoundError("Excel file not found, loading from CSV files")
    except:
        # Load from CSV files and normalize the result
        data = load_data_from_csv()

        for key, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                if 'country' in df.columns:
                    try:
                        df['country'] = df['country'].astype(str).str.strip().str.capitalize()
                    except Exception:
                        pass

                date_cols = [c for c in df.columns if 'date' in str(c).lower()]
                for c in date_cols:
                    try:
                        df[c] = pd.to_datetime(df[c], errors='coerce')
                    except Exception:
                        pass

                # --- Derived / precomputed columns for performance ---
                try:
                    import numpy as _np

                    # Add date-derived short formats to all dataframes where possible
                    for key, df in data.items():
                        if isinstance(df, pd.DataFrame) and not df.empty:
                            if 'date' in df.columns and pd.api.types.is_datetime64_any_dtype(df['date']):
                                try:
                                    df['date_YY'] = df['date'].dt.year
                                    df['date_MMYY'] = df['date'].dt.strftime('%m-%y')
                                except Exception:
                                    pass

                    # Compute NRW once for w_service
                    if 'w_service' in data and isinstance(data['w_service'], pd.DataFrame) and not data['w_service'].empty:
                        wdf = data['w_service']
                        if 'w_supplied' in wdf.columns and 'total_consumption' in wdf.columns:
                            try:
                                # Ensure numeric
                                wdf['w_supplied'] = pd.to_numeric(wdf['w_supplied'], errors='coerce')
                                wdf['total_consumption'] = pd.to_numeric(wdf['total_consumption'], errors='coerce')
                                # Vectorized NRW calculation, guard division by zero
                                wdf['NRW'] = _np.where(
                                    (wdf['w_supplied'].notna()) & (wdf['w_supplied'] != 0),
                                    ((wdf['w_supplied'] - wdf['total_consumption']) / wdf['w_supplied']) * 100,
                                    _np.nan
                                )
                                wdf['NRW'] = wdf['NRW'].round(2)
                                data['w_service'] = wdf
                            except Exception:
                                pass

                    # Compute Revenue Collection Efficiency for financial data
                    if 'all_fin_service' in data and isinstance(data['all_fin_service'], pd.DataFrame) and not data['all_fin_service'].empty:
                        fdf = data['all_fin_service']
                        # Try to merge billing water_billed if missing
                        if 'sewer_revenue' in fdf.columns or 'water_revenue' in fdf.columns:
                            try:
                                # Normalize numeric columns
                                for col in ['sewer_revenue', 'water_revenue', 'sewer_billed', 'water_billed']:
                                    if col in fdf.columns:
                                        fdf[col] = pd.to_numeric(fdf[col], errors='coerce').fillna(0)
                                    else:
                                        fdf[col] = 0

                                # If billing data exists, try to fill missing billed amounts
                                if 'billing' in data and isinstance(data['billing'], pd.DataFrame) and not data['billing'].empty:
                                    bdf = data['billing']
                                    if 'billed' in bdf.columns:
                                        # Merge on date and country if possible, else skip
                                        if 'date' in fdf.columns and 'date' in bdf.columns and 'country' in fdf.columns and 'country' in bdf.columns:
                                            try:
                                                merged = fdf.merge(
                                                    bdf[['date', 'country', 'billed']].rename(columns={'billed': 'water_billed'}),
                                                    on=['date', 'country'], how='left'
                                                )
                                                # Use billing's billed if fdf.water_billed is zero
                                                if 'water_billed' in merged.columns:
                                                    merged['water_billed'] = merged['water_billed'].fillna(0)
                                                    merged['water_billed'] = _np.where(merged['water_billed'] > 0, merged['water_billed'], merged.get('water_billed', 0))
                                                    fdf = merged
                                            except Exception:
                                                pass

                                fdf['total_revenue'] = fdf.get('sewer_revenue', 0) + fdf.get('water_revenue', 0)
                                fdf['total_billed'] = fdf.get('sewer_billed', 0) + fdf.get('water_billed', 0)

                                fdf['Revenue_Collection_Efficiency'] = _np.where(
                                    (fdf['total_billed'].notna()) & (fdf['total_billed'] != 0),
                                    (fdf['total_revenue'] / fdf['total_billed']) * 100,
                                    _np.nan
                                )
                                fdf['Revenue_Collection_Efficiency'] = fdf['Revenue_Collection_Efficiency'].round(2)
                                data['all_fin_service'] = fdf
                            except Exception:
                                pass
                except Exception:
                    # If anything goes wrong here, fall back to returning raw data
                    return data

                # After processing, try saving per-table parquet files for faster subsequent loads
                try:
                    if _HAS_PARQUET:
                        processed_dir = Path('Raw_Data/processed')
                        processed_dir.mkdir(parents=True, exist_ok=True)
                        for key, df in data.items():
                            try:
                                if isinstance(df, pd.DataFrame):
                                    df.to_parquet(processed_dir / f"{key}.parquet", index=False)
                            except Exception:
                                # ignore per-table write errors
                                pass
                        # write marker timestamp
                        with open(processed_dir / 'processed.timestamp', 'w') as fh:
                            fh.write(str(time.time()))
                except Exception:
                    pass

                return data


def get_country_list(data_dict):
    """Get list of available countries from loaded data"""
    for df in data_dict.values():
        if not df.empty and 'country' in df.columns:
            return sorted(df['country'].unique())
    return ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']


def regenerate_processed_cache(verbose: bool = True):
    """Force regenerating the per-table parquet cache from source CSV/Excel files.

    This function will load from Excel (if present and non-empty) or CSVs, normalize
    the data (dates/country casing), compute derived columns and write per-table
    parquet files into Raw_Data/processed/ along with a processed.timestamp marker.

    Returns a dict of written file paths.
    """
    processed_dir = Path('Raw_Data/processed')
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Prefer Excel if valid and non-empty
    try:
        data = {}
        if os.path.exists('Raw_Data/Master_Data.xlsx'):
            # try to load sheets
            try:
                data = {
                    'all_fin_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='all_fin_service'),
                    'all_national': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='all_national'),
                    'billing': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='billing'),
                    'production': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='production'),
                    's_access': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='s_access'),
                    's_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='s_service'),
                    'w_access': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='w_access'),
                    'w_service': pd.read_excel('Raw_Data/Master_Data.xlsx', sheet_name='w_service')
                }
                # If all sheets empty fallback to CSVs
                all_empty = all(isinstance(df, pd.DataFrame) and df.empty for df in data.values())
                if all_empty:
                    raise Exception("Excel sheets empty")
            except Exception:
                data = load_data_from_csv()
        else:
            data = load_data_from_csv()

        # Normalize and compute derived columns similar to load_all_data
        for key, df in data.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                try:
                    if 'country' in df.columns:
                        df['country'] = df['country'].astype(str).str.strip().str.capitalize()
                except Exception:
                    pass

                date_cols = [c for c in df.columns if 'date' in str(c).lower()]
                for c in date_cols:
                    try:
                        df[c] = pd.to_datetime(df[c], errors='coerce')
                    except Exception:
                        pass

        # compute NRW and revenue efficiency where applicable
        try:
            import numpy as _np
            if 'w_service' in data and isinstance(data['w_service'], pd.DataFrame) and not data['w_service'].empty:
                wdf = data['w_service']
                if 'w_supplied' in wdf.columns and 'total_consumption' in wdf.columns:
                    wdf['w_supplied'] = pd.to_numeric(wdf['w_supplied'], errors='coerce')
                    wdf['total_consumption'] = pd.to_numeric(wdf['total_consumption'], errors='coerce')
                    wdf['NRW'] = _np.where((wdf['w_supplied'].notna()) & (wdf['w_supplied'] != 0), ((wdf['w_supplied'] - wdf['total_consumption']) / wdf['w_supplied']) * 100, _np.nan)
                    wdf['NRW'] = wdf['NRW'].round(2)
                    data['w_service'] = wdf

            if 'all_fin_service' in data and isinstance(data['all_fin_service'], pd.DataFrame) and not data['all_fin_service'].empty:
                fdf = data['all_fin_service']
                for col in ['sewer_revenue', 'water_revenue', 'sewer_billed', 'water_billed']:
                    if col in fdf.columns:
                        fdf[col] = pd.to_numeric(fdf[col], errors='coerce').fillna(0)
                    else:
                        fdf[col] = 0

                fdf['total_revenue'] = fdf.get('sewer_revenue', 0) + fdf.get('water_revenue', 0)
                fdf['total_billed'] = fdf.get('sewer_billed', 0) + fdf.get('water_billed', 0)
                fdf['Revenue_Collection_Efficiency'] = _np.where((fdf['total_billed'].notna()) & (fdf['total_billed'] != 0), (fdf['total_revenue'] / fdf['total_billed']) * 100, _np.nan)
                fdf['Revenue_Collection_Efficiency'] = fdf['Revenue_Collection_Efficiency'].round(2)
                data['all_fin_service'] = fdf
        except Exception:
            pass

        written = {}
        for key, df in data.items():
            try:
                target = processed_dir / f"{key}.parquet"
                # write even empty frames - deterministic
                df.to_parquet(target, index=False)
                written[key] = str(target)
                if verbose:
                    print(f"Wrote {target}")
            except Exception as e:
                if verbose:
                    print(f"Skipped writing {key}: {e}")

        with open(processed_dir / 'processed.timestamp', 'w') as fh:
            fh.write(str(time.time()))

        return written
    except Exception as e:
        if verbose:
            print('Failed to regenerate cache:', e)
        return {}
