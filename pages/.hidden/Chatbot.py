import streamlit as st
from utils.data_loader import load_all_data
from utils import chatbot
import os
import re
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Chatbot", layout="wide")

# Modern pastel design
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
    
    h1 { 
        font-size: 2.8rem; 
        font-weight: 600; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
    }
    
    h3 { 
        font-size: 0.875rem; 
        font-weight: 600; 
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-top: 2.5rem;
    }
    
    .stChatMessage { 
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 16px; 
        padding: 1.5rem; 
        margin: 0.8rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }
    
    [data-testid="stSidebar"] { 
        background: linear-gradient(180deg, #faf5ff 0%, #f3e8ff 100%);
        border-right: 1px solid rgba(167, 139, 250, 0.2);
    }
    
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 { 
        color: #78716c; 
        font-size: 0.75rem; 
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    
    .stTextInput label, .stSlider label, .stCheckbox label { 
        color: #475569; 
        font-weight: 500; 
        font-size: 0.875rem;
    }
    
    .stTextInput > div > div { 
        background: #ffffff;
        border: 1px solid #cbd5e0; 
        border-radius: 8px;
    }
    
    .stButton > button { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; 
        border: none; 
        border-radius: 12px; 
        padding: 0.65rem 1.8rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover { 
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    [data-testid="stPlotlyChart"] { 
        background: #ffffff;
        padding: 1rem; 
        border-radius: 12px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        border: none;
    }
    
    .stSuccess { 
        border-radius: 8px; 
        border-left: 4px solid #10b981;
        background: #d1fae5;
    }
    
    .stInfo { 
        border-radius: 8px; 
        border-left: 4px solid #3b82f6;
        background: #eff6ff;
    }
    
    .stWarning { 
        border-radius: 8px; 
        border-left: 4px solid #f59e0b;
        background: #fffbeb;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI Assistant")

with st.sidebar:
    st.header("Chat Settings")
    api_key_input = st.text_input("API Key (Groq gsk_... — optional; or set env)", type='password')
    top_k = st.slider("Retriever: top K documents", min_value=1, max_value=10, value=4)
    include_graph = st.checkbox("Generate Graph", value=False, help="Ask the chatbot to generate a visualization along with the answer.")
    if st.button("Rebuild chat index (may take time)"):
        with st.spinner("Loading data and building index..."):
            dfs = load_all_data()
            info = chatbot.build_index_from_dataframes(dfs, persist=True)
        st.success(f"Index built: {info.get('n_docs', 0)} documents")

if 'history' not in st.session_state:
    st.session_state.history = []  # list of dicts: {'q','answer','insight','sources'}

if 'chat_input' not in st.session_state:
    st.session_state.chat_input = ''

# Suggested example questions to help users
suggested_questions = [
    "Which country has the highest revenue collection efficiency?",
    "Summarize financial health by country.",
    "Show top 5 rows with highest non-revenue water (NRW).",
    "What are the top revenue sources for Malawi?",
    "List months with the largest drop in production for Uganda."
]

st.markdown("**Try one of these example questions:**")
btn_cols = st.columns(len(suggested_questions))
for c, q in zip(btn_cols, suggested_questions):
    if c.button(q):
        # populate the session state so the input shows the value on next render
        st.session_state.chat_input = q

col1, col2 = st.columns([4,1])
with col1:
    user_q = st.text_input("Ask a question about the datasets and dashboard:", key='chat_input')
with col2:
    if st.button("Ask"):
        # no-op: handled by the presence of user_q below
        pass

if user_q:
    key = api_key_input or os.environ.get('GOOGLE_API_KEY')
    if not key:
        st.warning("No Google API key provided. Showing top-matching rows and a quick insight as a fallback (no LLM call).")
        with st.spinner("Retrieving local context..."):
            docs = chatbot.get_top_docs(user_q, top_k=top_k)
            # Build a simple fallback answer summarizing the retrieved snippets and compute insights
            if docs:
                snippets = []
                for s in docs:
                    meta = s.get('meta', {})
                    snippets.append(f"[{meta.get('source')}:{meta.get('row_index')}] {s.get('text')}")
                fallback_answer = "Top matching rows:\n\n" + "\n\n".join(snippets)
            else:
                fallback_answer = "No matching rows found in the local index. Please rebuild the index or provide an API key to call the LLM."
            insight = chatbot.summarize_docs_insights(docs)
            res = {'answer': fallback_answer, 'sources': docs, 'insight': insight}
            st.session_state.history.append({'q': user_q, 'answer': res['answer'], 'insight': res.get('insight'), 'sources': res.get('sources', [])})
    else:
        with st.spinner("Retrieving context and asking the model..."):
            # Load data for graph generation context if needed
            dfs = {}
            table_schemas = {}
            if include_graph:
                dfs = load_all_data()
                # Create a schema dict: table_name -> list of columns
                for name, df in dfs.items():
                    if isinstance(df, pd.DataFrame):
                        table_schemas[name] = list(df.columns)

            res = chatbot.answer_query(user_q, top_k=top_k, api_key=key, include_graph=include_graph, table_schemas=table_schemas)
            
            # Extract graph code if present
            answer_text = res['answer']
            graph_code = None
            
            # Regex to find ```python:graph ... ``` blocks
            code_match = re.search(r'```python:graph\n(.*?)\n```', answer_text, re.DOTALL)
            if code_match:
                graph_code = code_match.group(1)
                # Remove the code block from the answer text for cleaner display
                # answer_text = re.sub(r'```python:graph\n.*?\n```', '', answer_text, flags=re.DOTALL).strip()
                # Actually, keeping it might be fine, or we can just show the graph below.
                pass

            # ensure insight is present (LLM may include), but also compute a deterministic insight summary
            if 'insight' not in res or not res.get('insight'):
                res['insight'] = chatbot.summarize_docs_insights(res.get('sources', []))
            
            st.session_state.history.append({
                'q': user_q, 
                'answer': answer_text, 
                'insight': res.get('insight'), 
                'sources': res.get('sources', []),
                'graph_code': graph_code
            })

st.markdown("---")
st.header("Conversation")
for entry in reversed(st.session_state.history):
    q = entry.get('q')
    a = entry.get('answer')
    insight = entry.get('insight')
    sources = entry.get('sources', [])
    graph_code = entry.get('graph_code')
    st.markdown(f"**Q:** {q}")
    if insight:
        with st.container():
            st.success("Insight")
            # `insight` may be either a string or a dict; render reasonably
            if isinstance(insight, str):
                st.markdown(insight)
            elif isinstance(insight, dict):
                # compact table-like rendering
                for k, v in insight.items():
                    st.markdown(f"- **{k}**: {v}")
    st.markdown("**A:**")
    # Render the main answer with preserved newlines
    st.markdown(a)

    if graph_code:
        try:
            # Execute graph code
            # We need 'dfs' and 'px' in the local scope
            dfs = load_all_data()
            local_scope = {'dfs': dfs, 'px': px, 'pd': pd}
            exec(graph_code, {}, local_scope)
            if 'fig' in local_scope:
                st.plotly_chart(local_scope['fig'], use_container_width=True)
            else:
                st.error("Graph generation failed: 'fig' variable not found in executed code.")
        except Exception as e:
            st.error(f"Error generating graph: {e}")
            st.code(graph_code, language='python')
    if sources:
        with st.expander("Sources / Context snippets"):
            for s in sources:
                meta = s.get('meta', {})
                score = s.get('score')
                st.write(f"- {meta.get('source')} row {meta.get('row_index')} (score={score:.3f})")
                st.write(s.get('text'))
    st.markdown('---')

st.info("Tip: Use the sidebar to rebuild the index after you update data. The first build may take some time.")
