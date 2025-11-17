"""
Centralized data loading module with caching for optimal performance
"""
import streamlit as st
import pandas as pd
import os
from pathlib import Path


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
                df = pd.read_csv(country_path / f'billing_{country}.csv')
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

        return data


def get_country_list(data_dict):
    """Get list of available countries from loaded data"""
    for df in data_dict.values():
        if not df.empty and 'country' in df.columns:
            return sorted(df['country'].unique())
    return ['Cameroon', 'Lesotho', 'Malawi', 'Uganda']
