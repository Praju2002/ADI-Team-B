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

def test_fix():
    print("Testing Graph Aggregation Fix...")
    
    # Load data to pass table names
    dfs = load_all_data()
    table_names = list(dfs.keys())

    query = "Plot the total billed amount by country."
    try:
        print(f"Query: {query}")
        result = answer_query(query, include_graph=True, table_names=table_names)
        
        answer = result.get('answer', '')
        
        # Check for code block
        code_match = re.search(r'```python:graph\n(.*?)\n```', answer, re.DOTALL)
        if code_match:
            graph_code = code_match.group(1)
            print("Code generated:\n", graph_code)
            
            if "groupby" in graph_code or "pivot_table" in graph_code or "sum()" in graph_code:
                print("SUCCESS: Code contains aggregation logic.")
            else:
                print("WARNING: Code might not contain aggregation logic. Check manually.")
                
            # Try executing
            try:
                local_scope = {'dfs': dfs, 'px': px, 'pd': pd}
                exec(graph_code, {}, local_scope)
                if 'fig' in local_scope:
                    print("SUCCESS: 'fig' object created.")
                else:
                    print("FAILED: 'fig' object not found.")
            except Exception as e:
                print(f"FAILED: Error executing graph code: {e}")
        else:
            print("FAILED: No graph code block found.")

    except Exception as e:
        print(f"FAILED: Exception occurred: {e}")

if __name__ == "__main__":
    test_fix()
