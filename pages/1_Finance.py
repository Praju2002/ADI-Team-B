import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import warnings
import matplotlib.pyplot as plt
from utils.floating_button import add_floating_chatbot_button

warnings.filterwarnings('ignore')

# ---------------------------#
# Page Setup - Simplified Currency
# ---------------------------#
# NOTE: All financial values are treated as USD for simplicity
# Local currency conversions are not applied

def format_currency(amount, show_detailed=False):
    """Format currency as USD - simplified version"""
    if pd.isna(amount):
        return "N/A"
    return f"${amount:,.0f}"

def get_primary_country(df):
    """Get primary country from dataframe"""
    if df.empty or 'country' not in df.columns:
        return 'No Country'
    countries = [c for c in df['country'].dropna().unique() if str(c).strip()]
    return countries[0] if len(countries) >= 1 else 'No Country'

# ---------------------------#
# Streamlit Page Setup
# ---------------------------#
st.set_page_config(
    page_title="Water Utility Financial Health Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure browser resolves Streamlit runtime assets from root when pages are navigated
st.markdown("<base href='/' />", unsafe_allow_html=True)

# ---------------------------#
# Modern Pastel Design
# ---------------------------#
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
    
    * { 
        font-family: 'Poppins', 'Inter', -apple-system, sans-serif;
        transition: all 0.2s ease;
    }
    
    .main { 
        padding: 2rem 3rem; 
        background: linear-gradient(135deg, #fdfbfb 0%, #f7f4f9 100%);
        min-height: 100vh;
    }
    
    h1, h2 { 
        font-size: 2.8rem; 
        font-weight: 600; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }
    
    h3 { 
        font-size: 0.875rem; 
        font-weight: 600; 
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 2.5rem;
    }
    
    [data-testid="stMetricValue"] { 
        font-size: 2rem; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] { 
        color: #9ca3af; 
        font-size: 0.75rem; 
        font-weight: 500; 
        text-transform: uppercase; 
        letter-spacing: 0.08em;
    }
    
    [data-testid="metric-container"] { 
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(12px);
        padding: 1.8rem; 
        border-radius: 18px; 
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #faf5ff 0%, #f3e8ff 100%);
        border-right: 1px solid rgba(167, 139, 250, 0.2);
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 { 
        color: #334155; 
        font-size: 0.75rem; 
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stSelectbox label, .stRadio label { 
        color: #475569; 
        font-weight: 500; 
        font-size: 0.875rem;
    }
    
    .stSelectbox > div > div { 
        background: #ffffff;
        border: 1px solid #cbd5e0; 
        border-radius: 8px;
    }
    
    [data-testid="stPlotlyChart"] { 
        background: #ffffff;
        padding: 1rem; 
        border-radius: 12px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: none;
    }
    
    hr { 
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }
    
    [data-testid="column"] { padding: 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ---------------------------#
# Financial Health Analyzer Class
# ---------------------------#
class FinancialHealthAnalyzer:
    def __init__(self):
        self.data = {}
        self.load_data()

    @staticmethod
    def _safe_div(a, b, default=0):
        """Safe division to handle zero/NaN."""
        try:
            if pd.isna(a) or pd.isna(b) or b == 0:
                return default
            return a / b
        except Exception:
            return default

    @staticmethod
    def _parse_dates(series):
        """Flexible date parsing."""
        if series is None:
            return series
        s = series.astype(str).str.strip()
        formats = [
            '%b-%y', '%b-%Y', '%d-%m-%y', '%d-%m-%Y', '%m-%d-%y', '%m-%d-%Y',
            '%Y-%m-%d', '%d/%m/%y', '%d/%m/%Y', '%m/%d/%y', '%m/%d/%Y'
        ]
        best = pd.to_datetime(s, errors='coerce', dayfirst=True, infer_datetime_format=True)
        best_count = best.notna().sum()
        for fmt in formats:
            parsed = pd.to_datetime(s, format=fmt, errors='coerce')
            if parsed.notna().sum() > best_count:
                best, best_count = parsed, parsed.notna().sum()
                if best_count == len(s):
                    break
        return best

    def load_data(self):
        """Load CSV files for each country and dataset type."""
        try:
            # Use centralized loader so formats (country casing, dates) are consistent
            from utils.data_loader import load_all_data
            all_data = load_all_data()
            # Ensure we provide a consistent 'date' column (coerced to datetime)
            for key_map, target in (('all_fin_service', 'financial_services'),
                                    ('all_national', 'national_accounts'),
                                    ('billing', 'billing')):
                df = all_data.get(key_map, pd.DataFrame()).copy()
                if isinstance(df, pd.DataFrame) and not df.empty:
                    # If there is no explicit 'date' column, try to find a date-like column
                    if 'date' not in df.columns:
                        date_cols = [c for c in df.columns if 'date' in str(c).lower()]
                        if date_cols:
                            try:
                                df['date'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
                            except Exception:
                                df['date'] = pd.NaT
                    else:
                        # Coerce existing 'date' column to datetime
                        try:
                            df['date'] = pd.to_datetime(df['date'], errors='coerce')
                        except Exception:
                            df['date'] = pd.NaT

                    # Normalize country column name if variants exist (e.g., 'Country') and ensure values are strings
                    country_cols = [c for c in df.columns if str(c).strip().lower() == 'country']
                    if country_cols:
                        try:
                            df['country'] = df[country_cols[0]].astype(str).str.strip().str.capitalize()
                        except Exception:
                            df['country'] = df[country_cols[0]]

                self.data[target] = df
        except Exception as e:
            st.error(f"Error loading data: {e}")

    def calculate_financial_metrics(self, df):
        """
        Calculate comprehensive financial metrics using SEWER data.
        OpEx and revenue are all from utility-level sewer services.
        NOTE: All financial columns are treated as USD for consistency
        """
        if df.empty:
            return {
                'collection_ratio': 0,
                'opex_ratio': np.nan,
                'profit': 0,
                'profit_margin': np.nan,
                'revenue_per_km': 0,
                'total_billed': 0,
                'total_revenue': 0,
                'total_opex': 0
            }

        # Get totals from sewer data - treated as USD
        total_billed = df['sewer_billed'].sum() if 'sewer_billed' in df.columns else 0
        total_revenue = df['sewer_revenue'].sum() if 'sewer_revenue' in df.columns else 0
        total_opex = df['opex'].sum() if 'opex' in df.columns else 0
        total_sewer_length = df['sewer_length'].sum() if 'sewer_length' in df.columns else 0

        # Collection ratio = revenue collected / amount billed
        profit = total_revenue - total_opex

        # NOTE: return opex ratios as fractions (0..1). UI will format as percent where needed.
        return {
            'collection_ratio': self._safe_div(total_revenue, total_billed),
            'opex_ratio': self._safe_div(total_opex, total_revenue, np.nan),
            'profit': profit,
            'profit_margin': self._safe_div(profit, total_revenue, np.nan),
            'revenue_per_km': self._safe_div(total_revenue, total_sewer_length),
            'total_billed': total_billed,
            'total_revenue': total_revenue,
            'total_opex': total_opex,
            # opex_coverage kept as fraction for consistent formatting in UI
            'opex_coverage': self._safe_div(total_opex, total_revenue, np.nan)
        }

    def calculate_water_metrics(self, production_df, service_df):
        """Calculate water-specific metrics - minimal for financial purposes"""
        # Return empty metrics since we removed NRW/quality from financial dashboard
        return {
            'total_produced': 0,
            'total_supplied': 0,
            'total_consumed': 0,
            'nrw_volume': 0,
            'nrw_percentage': 0,
            'metering_rate': 0,
            'water_quality_chlorine': 0,
            'water_quality_ecoli': 0
        }

    def calculate_billing_metrics(self, df):
        """Calculate customer billing metrics from billing dataset"""
        if df.empty:
            return {
                'total_billed': 0,
                'total_paid': 0,
                'billing_collection_ratio': 0,
                'avg_consumption': 0,
                'avg_bill_amount': 0,
                'avg_payment_amount': 0,
                'payment_rate': 0
            }

        billed = df['billed'] if 'billed' in df.columns else pd.Series(dtype=float)
        paid = df['paid'] if 'paid' in df.columns else pd.Series(dtype=float)
        consumption = df['consumption_m3'] if 'consumption_m3' in df.columns else pd.Series(dtype=float)

        total_billed = billed.sum()
        total_paid = paid.sum()
        avg_consumption = consumption.mean() if not consumption.empty else 0
        avg_bill_amount = billed.mean() if not billed.empty else 0
        avg_payment_amount = paid.mean() if not paid.empty else 0
        payment_rate = (paid > 0).mean() if not paid.empty else 0

        return {
            'total_billed': total_billed,
            'total_paid': total_paid,
            'billing_collection_ratio': self._safe_div(total_paid, total_billed),
            'avg_consumption': avg_consumption,
            'avg_bill_amount': avg_bill_amount,
            'avg_payment_amount': avg_payment_amount,
            'payment_rate': payment_rate
        }


# ---------------------------#
# Dashboard Layout
# ---------------------------#
def main():
    st.markdown('<h1 class="main-header"> Water Utility Financial Dashboard</h1>', unsafe_allow_html=True)
    analyzer = FinancialHealthAnalyzer()

    # Sidebar: Filters
    st.sidebar.header("Filter Options")
    # Build a cleaned list of available countries and exclude empty/n_a placeholders
    raw_countries = [c for df in analyzer.data.values() if not df.empty and 'country' in df.columns for c in df['country'].unique()]
    cleaned = []
    for c in raw_countries:
        try:
            if pd.isna(c):
                continue
        except Exception:
            pass
        s = str(c).strip()
        if s == "" or s.lower() in ("nan", "n/a", "<n/a>", "<na>", "na", "none"):
            continue
        cleaned.append(s)

    available_countries = sorted(set(cleaned))

    # Use a single-dropdown with only real countries (no 'All Countries')
    if not available_countries:
        available_countries = ['No countries found']
    selected_country = st.sidebar.selectbox(
        "Select Country",
        options=available_countries,
        index=0,
        help="Select a country to filter the dashboard (single selection)"
    )
    
    st.sidebar.markdown("---")
    
    # Enhanced date filtering with slider
    date_min = min((df['date'].min() for df in analyzer.data.values() if not df.empty and 'date' in df.columns), default=None)
    date_max = max((df['date'].max() for df in analyzer.data.values() if not df.empty and 'date' in df.columns), default=None)
    
    if date_min and date_max:
        st.sidebar.markdown("### Time Period")
        # Quick period selection
        period_option = st.sidebar.radio(
            "Select Period:",
            ["All Time", "Last 12 Months", "Last 6 Months", "Custom Range"],
            index=0,
            help="Choose a time period to analyze"
        )
        
        if period_option == "Last 12 Months":
            date_range = (date_max - pd.DateOffset(months=12), date_max)
        elif period_option == "Last 6 Months":
            date_range = (date_max - pd.DateOffset(months=6), date_max)
        elif period_option == "Custom Range":
            date_range = st.sidebar.date_input("Select Date Range:", value=(date_min, date_max))
        else:
            date_range = (date_min, date_max)
    else:
        date_range = None

    # Apply filters
    filtered_data = {}
    for key, df in analyzer.data.items():
        if not df.empty:
            fdf = df.copy()
            # Apply single-country filter (exact match). If placeholder present, skip filtering.
            if selected_country and 'country' in fdf.columns and selected_country != 'No countries found':
                fdf = fdf[fdf['country'] == selected_country]
            if date_range and len(date_range) == 2 and 'date' in fdf.columns:
                start = pd.to_datetime(date_range[0]) if not isinstance(date_range[0], pd.Timestamp) else date_range[0]
                end = pd.to_datetime(date_range[1]) if not isinstance(date_range[1], pd.Timestamp) else date_range[1]
                fdf = fdf[(fdf['date'] >= start) & (fdf['date'] <= end)]
            filtered_data[key] = fdf

    # Display Overview
    display_overview_tab(filtered_data, analyzer)


# ---------------------------#
# Dashboard Sections
# ---------------------------#
def display_overview_tab(filtered_data, analyzer):
    """Financial health overview - focused on revenue collection and costs"""
    
   
    
    df = filtered_data.get('financial_services', pd.DataFrame())
    billing_df = filtered_data.get('billing', pd.DataFrame())
    
    if df.empty:
        st.warning("No financial services data available.")
        return
    
    # Calculate financial metrics using SEWER data
    metrics = analyzer.calculate_financial_metrics(df)
    billing_metrics = analyzer.calculate_billing_metrics(billing_df) if not billing_df.empty else {}
    
    # Get primary country for display
    primary_country = get_primary_country(df)
    
    # Multi-country notice
    countries_in_data = df['country'].unique() if 'country' in df.columns else []
  
    # ===========================
    # CRITICAL FINANCIAL HEALTH METRICS
    # ===========================
    st.markdown("###   Financial Health Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # 1. Sewer Collection Rate
    collection_ratio = metrics['collection_ratio']
    with col1:
        st.metric("Sewer Collection Rate", 
                 f"{collection_ratio:.1%}",
                 delta=f"{collection_ratio - 0.85:.1%} vs 85% target",
                 delta_color="normal" if collection_ratio >= 0.85 else "inverse",
                 help="Sewer revenue collected / Sewer billed (utility-level data)")
    
    # 2. Customer Payment Rate (collection efficiency)
    customer_collection = billing_metrics.get('billing_collection_ratio', 0)
    with col2:
        st.metric("Customer Payment Rate", 
                 f"{customer_collection:.1%}",
                 delta=f"{customer_collection - 0.85:.1%} vs 85% target",
                 delta_color="normal" if customer_collection >= 0.85 else "inverse",
                 help="Customer payments collected / Customer bills (water + sewer). Shows collection efficiency.")
    
    # 3. Operating Cost Ratio
    opex_coverage = metrics['opex_coverage']
    with col3:
        st.metric("Operating Cost Ratio", 
                 f"{opex_coverage:.1%}",
                 delta="Efficient" if opex_coverage <= 1 else "Over Budget",
                 delta_color="normal" if opex_coverage <= 1 else "inverse",
                 help="Operating costs / Sewer revenue. Target ≤100% (costs should not exceed revenue)")
    
    # 4. Profit Margin
    profit_val = metrics['profit']
    profit_margin = metrics['profit_margin']
    with col4:
        st.metric("Profit Margin", 
                 f"{profit_margin:.1%}" if not np.isnan(profit_margin) else "N/A",
                 delta="Profitable" if profit_val > 0 else "Loss",
                 delta_color="normal" if profit_val > 0 else "inverse",
                 help="Net profit as percentage of sewer revenue")
    
    # ===========================
    # FINANCIAL SUMMARY CARDS
    # ===========================
   
    
    # with col_e:
    #     customer_collection = billing_metrics.get('billing_collection_ratio', 0)
    #     cust_color = "#27ae60" if customer_collection >= 0.90 else "#f39c12" if customer_collection >= 0.75 else "#e74c3c"
    #     cust_bg = "#e8f8f0" if customer_collection >= 0.90 else "#fff3e0" if customer_collection >= 0.75 else "#fdecea"
    #     st.markdown(f"""
    #     <div style='background-color: {cust_bg}; padding: 1rem; border-radius: 8px; border-left: 4px solid {cust_color};'>
    #         <h4 style='margin: 0; color: #2c3e50;'>Customer Bills Paid</h4>
    #         <h2 style='margin: 0.5rem 0 0 0; color: {cust_color};'>{customer_collection:.1%}</h2>
    #         <p style='margin: 0; font-size: 0.9rem; color: #7f8c8d;'>Water + Sewer</p>
    #     </div>
    #     """, unsafe_allow_html=True)
    
    # ... REST OF THE CODE CONTINUES ...
    # Performance Assessment with better visuals
    st.markdown("---")
    st.markdown("### Performance Assessment")
    
    # Create progress bar style visualizations (more space efficient and cleaner)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Collection Rate - Bullet Chart Style
        st.markdown("**Collection Rate**")
        
        fig_bullet1 = go.Figure()
        
        # Background zones
        fig_bullet1.add_trace(go.Bar(
            y=['Performance'],
            x=[100],
            orientation='h',
            marker=dict(color='rgba(231, 76, 60, 0.15)'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_bullet1.add_trace(go.Bar(
            y=['Performance'],
            x=[15],
            orientation='h',
            marker=dict(color='rgba(243, 156, 18, 0.15)'),
            showlegend=False,
            hoverinfo='skip',
            base=70
        ))
        
        fig_bullet1.add_trace(go.Bar(
            y=['Performance'],
            x=[15],
            orientation='h',
            marker=dict(color='rgba(39, 174, 96, 0.15)'),
            showlegend=False,
            hoverinfo='skip',
            base=85
        ))
        
        # Actual value
        actual_color = "#27ae60" if collection_ratio >= 0.85 else "#f39c12" if collection_ratio >= 0.70 else "#e74c3c"
        fig_bullet1.add_trace(go.Bar(
            y=['Performance'],
            x=[collection_ratio * 100],
            orientation='h',
            marker=dict(color=actual_color),
            text=f"{collection_ratio:.1%}",
            textposition='inside',
            insidetextanchor='end',
            textfont=dict(color='white', size=14, family='Arial Black'),
            showlegend=False,
            hovertemplate=f"Collection Rate: {collection_ratio:.1%}<extra></extra>"
        ))
        
        # Target marker
        fig_bullet1.add_shape(
            type="line",
            x0=85, x1=85,
            y0=-0.4, y1=0.4,
            line=dict(color="#2c3e50", width=3)
        )
        
        fig_bullet1.add_annotation(
            x=85, y=0.5,
            text="Target",
            showarrow=False,
            font=dict(size=9, color="#2c3e50")
        )
        
        fig_bullet1.update_layout(
            barmode='overlay',
            height=120,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 100], showgrid=False, showticklabels=True, title=""),
            yaxis=dict(showticklabels=False, showgrid=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig_bullet1, use_container_width=True, key="bullet_collection_rate")
        st.markdown(f"<p style='text-align: center; color: {actual_color}; font-weight: 600;'>{'+' if collection_ratio >= 0.85 else ''}{(collection_ratio - 0.85):.1%} vs target</p>", unsafe_allow_html=True)
    
    with col2:
        # Payment Rate - Bullet Chart Style
        st.markdown("**Payment Rate**")
        
        fig_bullet2 = go.Figure()
        
        # Background zones
        fig_bullet2.add_trace(go.Bar(
            y=['Performance'],
            x=[100],
            orientation='h',
            marker=dict(color='rgba(231, 76, 60, 0.15)'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig_bullet2.add_trace(go.Bar(
            y=['Performance'],
            x=[20],
            orientation='h',
            marker=dict(color='rgba(243, 156, 18, 0.15)'),
            showlegend=False,
            hoverinfo='skip',
            base=60
        ))
        
        fig_bullet2.add_trace(go.Bar(
            y=['Performance'],
            x=[20],
            orientation='h',
            marker=dict(color='rgba(39, 174, 96, 0.15)'),
            showlegend=False,
            hoverinfo='skip',
            base=80
        ))
        
        # Actual value - use billing_collection_ratio instead of payment_rate
        customer_collection_val = billing_metrics.get('billing_collection_ratio', 0)
        payment_color = "#27ae60" if customer_collection_val >= 0.85 else "#f39c12" if customer_collection_val >= 0.70 else "#e74c3c"
        fig_bullet2.add_trace(go.Bar(
            y=['Performance'],
            x=[customer_collection_val * 100],
            orientation='h',
            marker=dict(color=payment_color),
            text=f"{customer_collection_val:.1%}",
            textposition='inside',
            insidetextanchor='end',
            textfont=dict(color='white', size=14, family='Arial Black'),
            showlegend=False,
            hovertemplate=f"Customer Collection Rate: {customer_collection_val:.1%}<extra></extra>"
        ))
        
        # Target marker
        fig_bullet2.add_shape(
            type="line",
            x0=85, x1=85,
            y0=-0.4, y1=0.4,
            line=dict(color="#2c3e50", width=3)
        )
        
        fig_bullet2.add_annotation(
            x=85, y=0.5,
            text="Target",
            showarrow=False,
            font=dict(size=9, color="#2c3e50")
        )
        
        fig_bullet2.update_layout(
            barmode='overlay',
            height=120,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 100], showgrid=False, showticklabels=True, title=""),
            yaxis=dict(showticklabels=False, showgrid=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig_bullet2, use_container_width=True, key="bullet_payment_rate")
        st.markdown(f"<p style='text-align: center; color: {payment_color}; font-weight: 600;'>{'+' if customer_collection_val >= 0.85 else ''}{(customer_collection_val - 0.85):.1%} vs target</p>", unsafe_allow_html=True)
    
    with col3:
        # Profit Margin - Bullet Chart Style
        st.markdown("**Profit Margin**")
        
        profit_display = max(min(profit_margin if not np.isnan(profit_margin) else 0, 0.50), -0.20)
        
        fig_bullet3 = go.Figure()
        
        # Background zones (shifted for negative values)
        fig_bullet3.add_trace(go.Bar(
            y=['Performance'],
            x=[20],
            orientation='h',
            marker=dict(color='rgba(231, 76, 60, 0.15)'),
            showlegend=False,
            hoverinfo='skip',
            base=-20
        ))
        
        fig_bullet3.add_trace(go.Bar(
            y=['Performance'],
            x=[15],
            orientation='h',
            marker=dict(color='rgba(243, 156, 18, 0.15)'),
            showlegend=False,
            hoverinfo='skip',
            base=0
        ))
        
        fig_bullet3.add_trace(go.Bar(
            y=['Performance'],
            x=[35],
            orientation='h',
            marker=dict(color='rgba(39, 174, 96, 0.15)'),
            showlegend=False,
            hoverinfo='skip',
            base=15
        ))
        
        # Actual value
        profit_color = "#27ae60" if profit_display >= 0.15 else "#f39c12" if profit_display >= 0 else "#e74c3c"
        fig_bullet3.add_trace(go.Bar(
            y=['Performance'],
            x=[profit_display * 100],
            orientation='h',
            marker=dict(color=profit_color),
            text=f"{profit_display:.1%}",
            textposition='inside',
            insidetextanchor='end' if profit_display > 0 else 'start',
            textfont=dict(color='white', size=14, family='Arial Black'),
            showlegend=False,
            hovertemplate=f"Profit Margin: {profit_display:.1%}<extra></extra>",
            base=0
        ))
        
        # Target marker
        fig_bullet3.add_shape(
            type="line",
            x0=15, x1=15,
            y0=-0.4, y1=0.4,
            line=dict(color="#2c3e50", width=3)
        )
        
        fig_bullet3.add_annotation(
            x=15, y=0.5,
            text="Target",
            showarrow=False,
            font=dict(size=9, color="#2c3e50")
        )
        
        # Zero line
        fig_bullet3.add_shape(
            type="line",
            x0=0, x1=0,
            y0=-0.4, y1=0.4,
            line=dict(color="#7f8c8d", width=2, dash="dash")
        )
        
        fig_bullet3.update_layout(
            barmode='overlay',
            height=120,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[-20, 50], showgrid=False, showticklabels=True, title=""),
            yaxis=dict(showticklabels=False, showgrid=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig_bullet3, use_container_width=True, key="bullet_profit_margin")
        st.markdown(f"<p style='text-align: center; color: {profit_color}; font-weight: 600;'>{'+' if profit_display >= 0.15 else ''}{(profit_display - 0.15):.1%} vs target</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Collection Trends Analysis
    st.markdown("### Collection Trends")
    
    # Prepare monthly data using SEWER data
    monthly = df.groupby(pd.Grouper(key='date', freq='M')).agg({
        'sewer_billed': 'sum',
        'sewer_revenue': 'sum',
        'opex': 'sum'
    }).reset_index()
    
    if len(monthly) > 0:
        # Calculate proper collection ratio: revenue / billed
        monthly['collection_ratio'] = (monthly['sewer_revenue'] / monthly['sewer_billed'] * 100).fillna(0)
        monthly['collection_gap'] = monthly['sewer_billed'] - monthly['sewer_revenue']
        monthly['profit'] = monthly['sewer_revenue'] - monthly['opex']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            
            # Show billed amount vs actual revenue collected
            fig.add_trace(go.Scatter(
                x=monthly['date'],
                y=monthly['sewer_billed'],
                name='Amount Billed',
                line=dict(color='#95a5a6', width=2),
                mode='lines',
                hovertemplate='Billed: %{y:$,.0f}<extra></extra>'
            ))
            
            # Add customdata for the gap hover
            monthly['gap_for_hover'] = monthly['sewer_billed'] - monthly['sewer_revenue']
            
            fig.add_trace(go.Scatter(
                x=monthly['date'],
                y=monthly['sewer_revenue'],
                name='Revenue Collected',
                line=dict(color='#27ae60', width=3),
                fill='tonexty',
                fillcolor='rgba(231, 76, 60, 0.15)',
                mode='lines',
                customdata=monthly[['gap_for_hover']].values,
                hovertemplate='Collected: %{y:$,.0f}<br>Gap (Uncollected): %{customdata[0]:$,.0f}<extra></extra>'
            ))
            
            # Target line (85% of billed)
            fig.add_trace(go.Scatter(
                x=monthly['date'],
                y=monthly['sewer_billed'] * 0.85,
                name='Target (85%)',
                line=dict(color='#3498db', width=1, dash='dash'),
                mode='lines',
                hovertemplate='Target: %{y:$,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                title="Billed vs. Collected Revenue (Gap in Red)",
                xaxis_title="Period",
                yaxis_title="Amount ($)",
                hovermode='x unified',
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=11),
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.05),
                    type="date",
                    gridcolor='#ecf0f1'
                ),
                yaxis=dict(gridcolor='#ecf0f1')
            )
            
            st.plotly_chart(fig, use_container_width=True, key="collection_billed_vs_collected")
        
        with col2:
            # Collection rate percentage
            fig2 = go.Figure()
            
            fig2.add_trace(go.Scatter(
                x=monthly['date'],
                y=monthly['collection_ratio'],
                mode='lines+markers',
                name='Collection Rate',
                line=dict(color='#3498db', width=2.5),
                marker=dict(size=6, color='#2980b9'),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ))
            
            # Performance zones
            fig2.add_hrect(y0=85, y1=100, fillcolor="#27ae60", opacity=0.08, line_width=0)
            fig2.add_hrect(y0=70, y1=85, fillcolor="#f39c12", opacity=0.08, line_width=0)
            fig2.add_hrect(y0=0, y1=70, fillcolor="#e74c3c", opacity=0.08, line_width=0)
            
            fig2.update_layout(
                title="Collection Rate Performance",
                xaxis_title="Period",
                yaxis_title="Rate (%)",
                yaxis_range=[0, 100],
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=11),
                xaxis=dict(
                    rangeslider=dict(visible=True, thickness=0.05),
                    type="date",
                    gridcolor='#ecf0f1'
                ),
                yaxis=dict(gridcolor='#ecf0f1')
            )
            
            st.plotly_chart(fig2, use_container_width=True, key="collection_rate_performance")
        
        # Insights below the charts
        # st.markdown("#### 📊 What This Tells Us")
        
        col1, col2, col3 = st.columns(3)
        
        # Calculate insights
        avg_collection = monthly['collection_ratio'].mean()
        total_gap = monthly['collection_gap'].sum()
        recent_avg = monthly.tail(3)['collection_ratio'].mean()
        older_avg = monthly.iloc[-6:-3]['collection_ratio'].mean() if len(monthly) >= 6 else recent_avg
        trend = recent_avg - older_avg
        
        with col1:
            st.markdown(f"""
            **Average Collection Rate**  
            {avg_collection:.1f}% of billed amounts are collected on average  
            {'🟢 Above target' if avg_collection >= 85 else '🟡 Below target' if avg_collection >= 70 else '🔴 Needs attention'}
            """)
        
        with col2:
            st.markdown(f"""
            **Total Uncollected Revenue**  
            {format_currency(total_gap)} in revenue gap over the period  
            
            """)
        
        with col3:
            arrow = "↑" if trend > 2 else "↓" if trend < -2 else "→"
            trend_text = "improving" if trend > 2 else "declining" if trend < -2 else "stable"
            st.markdown(f"""
            **Recent Trend**  
            {arrow} Collection rate is {trend_text}  
            {'+' if trend > 0 else ''}{trend:.1f}% change in recent months
            """)
        
        # Trend indicator
        if len(monthly) >= 6:
            trend_col1, trend_col2, trend_col3 = st.columns(3)
            with trend_col1:
                st.metric("Recent Average", f"{recent_avg:.1f}%")
            with trend_col2:
                arrow = "↗" if trend > 2 else "↘" if trend < -2 else "→"
                st.metric("Trend", f"{arrow} {abs(trend):.1f}%", delta=f"{trend:.1f}%")
            with trend_col3:
                volatility = monthly['collection_ratio'].std()
                st.metric("Volatility", f"±{volatility:.1f}%")
    
    st.markdown("---")
    
    # Profitability Analysis
    st.markdown("### Profitability Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig3 = go.Figure()

        # Simple grouped bar chart: Revenue vs OpEx on the same axis
        fig3.add_trace(go.Bar(
            x=monthly['date'],
            y=monthly['sewer_revenue'],
            name='Revenue',
            marker_color='#27ae60'
        ))

        fig3.add_trace(go.Bar(
            x=monthly['date'],
            y=monthly['opex'],
            name='Operating Costs',
            marker_color='#e74c3c'
        ))

        fig3.update_layout(
            title='Revenue vs. Operating Costs',
            barmode='group',
            xaxis_title="Period",
            yaxis_title="Amount ($)",
            height=400,
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=11),
            xaxis=dict(
                rangeslider=dict(visible=True, thickness=0.05),
                type="date",
                gridcolor='#ecf0f1'
            ),
            yaxis=dict(gridcolor='#ecf0f1'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig3, use_container_width=True, key="profitability_revenue_vs_opex")
    
    with col2:
        fig4 = go.Figure()
        
        colors = ['#27ae60' if p > 0 else '#e74c3c' for p in monthly['profit']]
        
        fig4.add_trace(go.Bar(
            x=monthly['date'],
            y=monthly['profit'],
            marker_color=colors,
            name='Profit/Loss',
            showlegend=False
        ))
        
        fig4.add_hline(y=0, line_dash="solid", line_color="#34495e", line_width=1.5)
        
        fig4.update_layout(
            title='Monthly Profit/Loss',
            xaxis_title="Period",
            yaxis_title="Profit/Loss ($)",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=11),
            xaxis=dict(
                rangeslider=dict(visible=True, thickness=0.05),
                type="date",
                gridcolor='#ecf0f1'
            ),
            yaxis=dict(gridcolor='#ecf0f1')
        )
        
        st.plotly_chart(fig4, use_container_width=True, key="profitability_profit_loss")
    
    # Calculate opex_ratio_pct
    monthly['opex_ratio_pct'] = (monthly['opex'] / monthly['sewer_revenue'] * 100).fillna(0)
    
    col1, col2, col3 = st.columns(3)
    
    total_opex = monthly['opex'].sum()
    total_revenue = monthly['sewer_revenue'].sum()
    avg_opex_ratio = monthly['opex_ratio_pct'].mean()
    
    with col1:
        st.metric(
            "Avg OpEx Ratio", 
            f"{avg_opex_ratio:.1f}%",
            delta=f"{(80 - avg_opex_ratio):.1f}% vs target",
            delta_color="normal" if avg_opex_ratio < 80 else "inverse"
        )
    
    with col2:
        st.metric(
            "Total OpEx",
            format_currency(total_opex),
            help="Total operational expenditure over the period"
        )
    
    with col3:
        efficiency_status = "🟢 Efficient" if avg_opex_ratio < 80 else "🟡 Monitor" if avg_opex_ratio < 100 else "🔴 At Risk"
        st.metric(
            "Efficiency Status",
            efficiency_status,
            help="Based on OpEx ratio: <80% = Efficient, 80-100% = Monitor, >100% = At Risk"
        )
    
    # Country Performance Comparison
    st.markdown("---")
    
    # ===========================
    # BUDGET MANAGEMENT & ALLOCATION
    # ===========================
    st.markdown("### Budget Management & Resource Allocation")
    
    df_national = filtered_data.get('national_accounts', pd.DataFrame())
    
    if not df_national.empty and 'budget_allocated' in df_national.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Budget Variance (Indicator #34)
            st.markdown("#### Budget Variance")
            if 'opex' in df.columns and 'date' in df_national.columns and 'date' in df.columns and 'country' in df.columns:
                try:
                    # Convert date columns to same format for merging
                    df_merge = df.copy()
                    df_nat_merge = df_national.copy()
                    
                    # Ensure date columns are datetime
                    df_merge['date'] = pd.to_datetime(df_merge['date'], errors='coerce')
                    df_nat_merge['date'] = pd.to_datetime(df_nat_merge['date'], errors='coerce')
                    
                    # Extract year for matching (national accounts is annual)
                    df_merge['year'] = df_merge['date'].dt.year
                    df_nat_merge['year'] = df_nat_merge['date'].dt.year
                    
                    # Merge on year and country
                    merged_budget = df_merge.merge(
                        df_nat_merge[['year', 'country', 'budget_allocated']],
                        on=['year', 'country'],
                        how='left'
                    )
                    
                    # Calculate budget variance - filter out zeros
                    merged_budget['actual_expenditure'] = pd.to_numeric(merged_budget['opex'], errors='coerce')
                    merged_budget['budget_allocated'] = pd.to_numeric(merged_budget['budget_allocated'], errors='coerce')
                    
                    # Filter valid records
                    valid_budget = merged_budget[
                        (merged_budget['budget_allocated'].notna()) & 
                        (merged_budget['budget_allocated'] > 0) &
                        (merged_budget['actual_expenditure'].notna()) &
                        (merged_budget['actual_expenditure'] > 0)
                    ].copy()
                    
                    if len(valid_budget) > 0:
                        # Aggregate by year since budget is annual
                        annual_budget = valid_budget.groupby('year').agg({
                            'budget_allocated': 'first',  # Budget is same for all months in year
                            'actual_expenditure': 'sum'   # Sum monthly opex
                        }).reset_index()
                        
                        total_allocated = annual_budget['budget_allocated'].sum()
                        total_spent = annual_budget['actual_expenditure'].sum()
                        variance = total_allocated - total_spent
                        variance_pct = (variance / total_allocated * 100) if total_allocated > 0 else 0
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Total Allocated", format_currency(total_allocated))
                        with col_b:
                            delta_color = "normal" if variance >= 0 else "inverse"
                            st.metric("Variance", format_currency(variance), delta=f"{variance_pct:.1f}%", delta_color=delta_color)
                        
                        # Budget variance trend by year
                        if len(annual_budget) > 0:
                            annual_budget['variance_pct'] = ((annual_budget['budget_allocated'] - annual_budget['actual_expenditure']) / annual_budget['budget_allocated']) * 100
                            
                            fig = go.Figure()
                            fig.add_trace(go.Bar(
                                x=annual_budget['year'],
                                y=annual_budget['budget_allocated'],
                                name='Allocated',
                                marker_color='#3498db'
                            ))
                            fig.add_trace(go.Bar(
                                x=annual_budget['year'],
                                y=annual_budget['actual_expenditure'],
                                name='Spent (OpEx)',
                                marker_color='#e74c3c'
                            ))
                            fig.update_layout(
                                title="Budget: Allocated vs Spent (Indicator #34)",
                                xaxis_title="Year",
                                yaxis_title="Amount ($)",
                                height=300,
                                barmode='group',
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig, use_container_width=True, key="budget_variance_trend")
                    else:
                        st.info("💡 Budget variance requires annual budget data and monthly OpEx data. Check if both are available for the selected period.")
                except Exception as e:
                    st.warning(f"Unable to calculate budget variance: {str(e)}")
            else:
                st.info("📊 Budget variance requires 'opex', 'date', and 'country' columns in both datasets.")
        
        with col2:
            # Budget Allocation Split (Indicators #39, #40)
            st.markdown("#### Budget Allocation: Sanitation vs Water")
            if 'san_allocation' in df_national.columns and 'wat_allocation' in df_national.columns:
                # Filter valid allocation data (non-zero, non-null)
                valid_san = df_national['san_allocation'].replace(0, pd.NA).dropna()
                valid_wat = df_national['wat_allocation'].replace(0, pd.NA).dropna()
                
                if len(valid_san) > 0 and len(valid_wat) > 0:
                    avg_san = valid_san.mean()
                    avg_wat = valid_wat.mean()
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Sanitation Allocation", f"{avg_san:.1f}%", help="Indicator #40")
                    with col_b:
                        st.metric("Water Allocation", f"{avg_wat:.1f}%", help="Indicator #39")
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=['Sanitation', 'Water', 'Other'],
                        values=[avg_san, avg_wat, max(0, 100 - avg_san - avg_wat)],
                        marker=dict(colors=['#e74c3c', '#3498db', '#95a5a6']),
                        hole=0.4
                    )])
                    fig.update_layout(
                        title="Budget Allocation Split",
                        height=300,
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True, key="budget_allocation_pie")
                else:
                    st.info("Budget allocation data not available for selected filters")
            else:
                st.info("Budget allocation columns not found in data")
    
    # ===========================
    # HUMAN CAPITAL DEVELOPMENT
    # ===========================
    st.markdown("---")
    st.markdown("###  Human Capital & Training Investment")
    st.caption("Available for: Cameroon, Lesotho, Malawi, Uganda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Training Investment (Indicator #51)
        if not df_national.empty and 'staff_training_budget' in df_national.columns and 'budget_allocated' in df_national.columns:
            # Filter valid data
            valid_nat = df_national[
                (df_national['staff_training_budget'].notna()) &
                (df_national['staff_training_budget'] > 0) &
                (df_national['budget_allocated'].notna()) &
                (df_national['budget_allocated'] > 0)
            ].copy()
            
            if len(valid_nat) > 0:
                total_training = valid_nat['staff_training_budget'].sum()
                total_budget = valid_nat['budget_allocated'].sum()
                training_pct = (total_training / total_budget * 100) if total_budget > 0 else 0
                
                if training_pct > 0:
                    delta_color = "normal" if training_pct >= 5 else "inverse"
                    st.metric(
                        "Training Investment %",
                        f"{training_pct:.2f}%",
                        delta=f"Target: >5%",
                        delta_color=delta_color,
                        help="Indicator #51: % of WASH budget invested in training"
                    )
                else:
                    st.info("Training budget data not available")
            else:
                st.info("Training budget data not available for selected filters")
        else:
            st.info("Training budget columns not found")
    
    with col2:
        # Trained Staff Count (Indicator #52)
        if not df_national.empty and 'trained_staff' in df_national.columns:
            valid_trained = df_national['trained_staff'].replace(0, pd.NA).dropna()
            
            if len(valid_trained) > 0:
                total_trained = valid_trained.sum()
                st.metric(
                    "Trained Staff Count",
                    f"{total_trained:,.0f}",
                    help="Indicator #52: Total trained personnel"
                )
            else:
                st.info("Trained staff data not available")
        else:
            st.info("Trained staff column not found")
    
    st.markdown("---")
    st.markdown("### Country Performance Comparison")
    
    # Country color palette inspired by flags
    country_colors = {
        'Cameroon': '#007A5E',
        'Lesotho': '#00209F',
        'Malawi': '#CE1126',
        'Uganda': '#FCDC04'
    }
    
    records = []
    for country in sorted(df['country'].dropna().unique()):
        cdf = df[df['country'] == country]
        cm = analyzer.calculate_financial_metrics(cdf)
        records.append({
            'Country': country,
            'Collection Rate': cm['collection_ratio'] * 100,
            'Profit Margin': cm['profit_margin'] * 100 if not np.isnan(cm['profit_margin']) else 0
        })
    
    if records:
        country_df = pd.DataFrame(records)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig5 = go.Figure()
            
            for idx, row in country_df.sort_values('Collection Rate').iterrows():
                fig5.add_trace(go.Bar(
                    y=[row['Country']],
                    x=[row['Collection Rate']],
                    orientation='h',
                    name=row['Country'],
                    marker_color=country_colors.get(row['Country'], '#3498db'),
                    text=f"{row['Collection Rate']:.1f}%",
                    textposition='outside',
                    showlegend=False
                ))
            
            # Add target line
            fig5.add_vline(x=85, line_dash="dash", line_color="#7f8c8d", 
                          annotation_text="Target: 85%", annotation_position="top")
            
            fig5.update_layout(
                title='Collection Rate by Country',
                xaxis_title="Collection Rate (%)",
                yaxis_title="",
                height=300,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=11),
                xaxis=dict(gridcolor='#ecf0f1', range=[0, 100]),
                margin=dict(l=100)
            )
            
            st.plotly_chart(fig5, use_container_width=True, key="country_collection_rate")
        
        with col2:
            fig6 = go.Figure()
            
            for idx, row in country_df.sort_values('Profit Margin').iterrows():
                fig6.add_trace(go.Bar(
                    y=[row['Country']],
                    x=[row['Profit Margin']],
                    orientation='h',
                    name=row['Country'],
                    marker_color=country_colors.get(row['Country'], '#3498db'),
                    text=f"{row['Profit Margin']:.1f}%",
                    textposition='outside',
                    showlegend=False
                ))
            
            # Add target line
            fig6.add_vline(x=15, line_dash="dash", line_color="#7f8c8d",
                          annotation_text="Target: 15%", annotation_position="top")
            
            fig6.update_layout(
                title='Profit Margin by Country',
                xaxis_title="Profit Margin (%)",
                yaxis_title="",
                height=300,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(size=11),
                xaxis=dict(gridcolor='#ecf0f1'),
                margin=dict(l=100)
            )
            
            st.plotly_chart(fig6, use_container_width=True, key="country_profit_margin")
        
        # Summary table
        st.markdown("#### Summary Metrics by Country")
        st.dataframe(
            country_df.style.background_gradient(subset=['Collection Rate', 'Profit Margin'], cmap='RdYlGn', vmin=0, vmax=100)
                            .format({
                                'Collection Rate': '{:.1f}%',
                                'Profit Margin': '{:.1f}%'
                            }),
            use_container_width=True,
            hide_index=True
        )


def display_trends_tab(filtered_data, analyzer, show_usd=False):
    """KEEPING ALL ORIGINAL FUNCTIONALITY - just added show_usd parameter"""
    st.header("Financial Trends Analysis")
    
    st.markdown("""
    Comprehensive trend analysis reveals patterns, identifies opportunities, and highlights areas requiring attention.
    Use the controls below to explore different time periods and metrics.
    """)
    
    df = filtered_data.get('financial_services', pd.DataFrame())
    
    if df.empty:
        st.warning("No financial data available.")
        return

    # ADDED: Get primary country
    primary_country = get_primary_country(df)

    # Aggregation selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        time_granularity = st.selectbox(
            "Time Period:",
            ["Monthly", "Quarterly", "Yearly"],
            index=0
        )
    
    with col2:
        metric_focus = st.selectbox(
            "Focus Metric:",
            ["All Metrics", "Collection Rate", "Profitability", "Operational Efficiency"],
            index=0
        )
    
    freq_map = {"Monthly": "M", "Quarterly": "Q", "Yearly": "Y"}
    freq = freq_map[time_granularity]
    
    monthly = df.groupby(pd.Grouper(key='date', freq=freq)).agg({
        'sewer_billed': 'sum',
        'sewer_revenue': 'sum',
        'opex': 'sum',
        'san_staff': 'mean',
        'w_staff': 'mean'
    }).reset_index()
    
    if len(monthly) == 0:
        st.warning("No data available for the selected period.")
        return
    
    # Calculate proper ratios using sewer billed vs collected amounts
    monthly['collection_ratio'] = (monthly['sewer_revenue'] / monthly['sewer_billed']).fillna(0)
    monthly['opex_ratio'] = (monthly['opex'] / monthly['sewer_revenue']).fillna(0)
    monthly['profit'] = monthly['sewer_revenue'] - monthly['opex']
    monthly['profit_margin'] = (monthly['profit'] / monthly['sewer_revenue']).fillna(0)
    monthly['total_staff'] = monthly['san_staff'] + monthly['w_staff']
    
    # ALL THE REST OF THE TRENDS TAB CODE REMAINS EXACTLY THE SAME
    # Just replace ylabel "Amount ($)" with dynamic currency where needed
    
    st.markdown("---")
    
    # Collection Rate Evolution
    if metric_focus in ["All Metrics", "Collection Rate"]:
        st.markdown("### Collection Rate Evolution")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=monthly['date'],
            y=monthly['collection_ratio'] * 100,
            mode='lines+markers',
            name='Collection Rate',
            line=dict(color='#3498db', width=2.5),
            marker=dict(size=8, color='#2980b9'),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        
        # Trend line
        if len(monthly) > 1:
            z = np.polyfit(range(len(monthly)), monthly['collection_ratio'] * 100, 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=monthly['date'],
                y=p(range(len(monthly))),
                mode='lines',
                name='Trend',
                line=dict(color='#e74c3c', width=1.5, dash='dash')
            ))
        
        # Performance zones
        fig.add_hrect(y0=85, y1=100, fillcolor="#27ae60", opacity=0.05, line_width=0)
        fig.add_hrect(y0=70, y1=85, fillcolor="#f39c12", opacity=0.05, line_width=0)
        fig.add_hrect(y0=0, y1=70, fillcolor="#e74c3c", opacity=0.05, line_width=0)
        
        fig.update_layout(
            xaxis_title=time_granularity,
            yaxis_title="Collection Rate (%)",
            height=450,
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=11),
            xaxis=dict(
                rangeslider=dict(visible=True, thickness=0.05),
                type="date",
                gridcolor='#ecf0f1'
            ),
            yaxis=dict(gridcolor='#ecf0f1')
        )
        
        st.plotly_chart(fig, use_container_width=True, key="trends_collection_rate_evolution")
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Average", f"{monthly['collection_ratio'].mean():.1%}")
        col2.metric("Best", f"{monthly['collection_ratio'].max():.1%}")
        col3.metric("Worst", f"{monthly['collection_ratio'].min():.1%}")
        col4.metric("Std Dev", f"{monthly['collection_ratio'].std():.1%}")
        
        st.markdown("---")
    
    # NOTE: All currency values are displayed in USD ($) for consistency
    # The format_currency() function handles all monetary formatting
    
    st.info("💡 **Note:** All financial values are displayed in USD for consistent comparison across countries")


# ---------------------------#
# Run App
# ---------------------------#
if __name__ == "__main__":
    main()
    # Add floating chatbot button
    add_floating_chatbot_button()