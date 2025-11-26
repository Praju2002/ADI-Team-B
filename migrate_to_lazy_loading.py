"""
Migration helper script to update remaining pages to use lazy loading.

This script shows the pattern for migrating Water.py, Sanitation.py, and Finance.py
"""

MIGRATION_PATTERN = """
# OLD PATTERN (to be replaced):
# ==================================
import streamlit as st
import pandas as pd
# ... other imports ...

@st.cache_data(ttl=3600)
def load_data_from_csv():
    # ... 100+ lines of loading logic ...
    return data

@st.cache_data(ttl=3600)
def load_all_data():
    # ... Excel/CSV fallback logic ...
    return data

data_dict = load_all_data()
all_fin_service_df = data_dict['all_fin_service']
all_national_df = data_dict['all_national']
# ... loading all 8 tables ...

# NEW PATTERN (optimized):
# ==================================
import streamlit as st
import pandas as pd
from utils.data_loader import load_table, get_country_list
# ... other imports ...

# Remove load_data_from_csv() function completely
# Remove load_all_data() function completely

# Load only tables needed for this specific page
@st.cache_data(ttl=3600)
def get_page_data():
    '''Load only the tables needed for this page'''
    return {
        # Only include tables this page actually uses
        'w_service': load_table('w_service'),
        'w_access': load_table('w_access'),
        'production': load_table('production'),
        # Don't load tables you don't need!
    }

data_dict = get_page_data()
w_service_df = data_dict['w_service']
w_access_df = data_dict['w_access']
production_df = data_dict['production']
# Only load what you need

# Get countries efficiently
available_countries = get_country_list('w_service')  # Much faster!
"""

EXAMPLE_MIGRATIONS = {
    'Water.py': """
# Water.py needs:
- production (for service_hours / Continuity of Supply)
- w_service (for Water Quality Compliance, Metering Ratio, NRW)
- all_fin_service (for Operating Cost Coverage)

@st.cache_data(ttl=3600)
def get_water_page_data():
    return {
        'production': load_table('production'),
        'w_service': load_table('w_service'),
        'all_fin_service': load_table('all_fin_service'),
    }

data_dict = get_water_page_data()
production_df = data_dict['production']
w_service_df = data_dict['w_service']
all_fin_service_df = data_dict['all_fin_service']
""",
    
    'Sanitation.py': """
# Sanitation.py needs:
- s_service (for Sewer Coverage, Wastewater Treatment, FS Management)
- all_fin_service (for Complaint Resolution)

@st.cache_data(ttl=3600)
def get_sanitation_page_data():
    return {
        's_service': load_table('s_service'),
        'all_fin_service': load_table('all_fin_service'),
    }

data_dict = get_sanitation_page_data()
s_service_df = data_dict['s_service']
all_fin_service_df = data_dict['all_fin_service']
""",
    
    'Finance.py': """
# Finance.py needs:
- all_fin_service (financial metrics)
- billing (customer billing)
- all_national (national accounts, if used)

@st.cache_data(ttl=3600)
def get_finance_page_data():
    return {
        'all_fin_service': load_table('all_fin_service'),
        'billing': load_table('billing'),
        'all_national': load_table('all_national'),
    }

data_dict = get_finance_page_data()
all_fin_service_df = data_dict['all_fin_service']
billing_df = data_dict['billing']
all_national_df = data_dict['all_national']
"""
}

def print_migration_guide():
    print("=" * 80)
    print("LAZY LOADING MIGRATION GUIDE")
    print("=" * 80)
    print()
    print(MIGRATION_PATTERN)
    print()
    print("=" * 80)
    print("SPECIFIC PAGE EXAMPLES")
    print("=" * 80)
    for page, example in EXAMPLE_MIGRATIONS.items():
        print(f"\n### {page}")
        print(example)
    print()
    print("=" * 80)
    print("STEPS TO MIGRATE:")
    print("=" * 80)
    print("""
1. Open the page file (e.g., Water.py)

2. Add import at top:
   from utils.data_loader import load_table, get_country_list

3. Delete these functions:
   - load_data_from_csv()
   - load_all_data()

4. Replace data loading section with lazy loading:
   - Create get_<page>_data() function
   - Only load tables the page actually uses
   - Use load_table() for each needed table

5. Update country list loading:
   OLD: sorted(df['country'].unique())
   NEW: get_country_list('table_name')

6. Test the page to ensure it works correctly

7. Check performance - page should load faster!
    """)
    print("=" * 80)

if __name__ == "__main__":
    print_migration_guide()
