import streamlit as st
from utils.data_loader import load_all_data
from utils import chatbot
import os
import re
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Chatbot", layout="wide")
st.title("🤖 Chat with the Dashboard Data")

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
