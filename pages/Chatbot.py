import streamlit as st
from utils.data_loader import get_data_lazy
from utils import chatbot
import os

st.set_page_config(page_title="Data Chatbot", layout="wide")
st.title("🤖 Chat with the Dashboard Data")

# Check if index exists
index_exists = chatbot.INDEX_DIR.exists() and all([
    (chatbot.INDEX_DIR / 'docs.pkl').exists(),
    (chatbot.INDEX_DIR / 'vectorizer.pkl').exists(),
    (chatbot.INDEX_DIR / 'matrix.npz').exists()
])

with st.sidebar:
    st.header("Chat Settings")
    api_key_input = st.text_input("Google API Key (optional, or set GOOGLE_API_KEY env)", type='password')
    top_k = st.slider("Retriever: top K documents", min_value=1, max_value=10, value=4)
    
    if not index_exists:
        st.warning("⚠️ Chat index not built yet. Click below to build it.")
    else:
        st.success("✅ Chat index ready")
    
    if st.button("Rebuild chat index" + (" (required)" if not index_exists else " (may take time)")):
        with st.spinner("Loading data and building index..."):
            # Use lazy loading - only load when building index
            dfs = {}
            lazy_data = get_data_lazy()
            for key in lazy_data.keys():
                dfs[key] = lazy_data[key]
            info = chatbot.build_index_from_dataframes(dfs, persist=True)
        st.success(f"Index built: {info.get('n_docs', 0)} documents")
        st.rerun()

if not index_exists:
    st.info("👆 Please build the chat index first using the button in the sidebar.")
    st.stop()

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
        st.session_state.chat_input = q
        st.experimental_rerun()

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
            res = chatbot.answer_query(user_q, top_k=top_k, api_key=key)
            # ensure insight is present (LLM may include), but also compute a deterministic insight summary
            if 'insight' not in res or not res.get('insight'):
                res['insight'] = chatbot.summarize_docs_insights(res.get('sources', []))
            st.session_state.history.append({'q': user_q, 'answer': res['answer'], 'insight': res.get('insight'), 'sources': res.get('sources', [])})

st.markdown("---")
st.header("Conversation")
for entry in reversed(st.session_state.history):
    q = entry.get('q')
    a = entry.get('answer')
    insight = entry.get('insight')
    sources = entry.get('sources', [])
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
    if sources:
        with st.expander("Sources / Context snippets"):
            for s in sources:
                meta = s.get('meta', {})
                score = s.get('score')
                st.write(f"- {meta.get('source')} row {meta.get('row_index')} (score={score:.3f})")
                st.write(s.get('text'))
    st.markdown('---')

st.info("Tip: Use the sidebar to rebuild the index after you update data. The first build may take some time.")
