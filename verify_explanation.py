import os
import re
import sys
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px

# Load env vars
load_dotenv()

# Add current dir to path so we can import utils
sys.path.append(os.getcwd())

from utils.chatbot import answer_query
from utils.data_loader import load_all_data

def test_explanation():
    print("Testing Graph Explanation Improvement...")
    
    # Load data to pass schemas
    dfs = load_all_data()
    table_schemas = {}
    for name, df in dfs.items():
        if isinstance(df, pd.DataFrame):
            table_schemas[name] = list(df.columns)

    query = "Plot the total billed amount by country."
    try:
        print(f"Query: {query}")
        result = answer_query(query, include_graph=True, table_schemas=table_schemas)
        
        answer = result.get('answer', '')
        print("\nAnswer received:\n")
        print(answer)
        
        # Check for explanation keywords
        if "visualizes" in answer.lower() or "x-axis" in answer.lower() or "y-axis" in answer.lower() or "shows" in answer.lower():
            print("\nSUCCESS: Answer seems to contain an explanation.")
        else:
            print("\nWARNING: Answer might lack detailed explanation.")

    except Exception as e:
        print(f"FAILED: Exception occurred: {e}")

if __name__ == "__main__":
    test_explanation()
