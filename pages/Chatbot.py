import streamlit as st
from utils.data_loader import load_all_data
from utils import chatbot
import os

st.set_page_config(page_title="Data Chatbot", layout="wide")
st.title("🤖 Chat with the Dashboard Data")

with st.sidebar:
    st.header("Chat Settings")
    api_key_input = st.text_input("Google API Key (optional, or set GOOGLE_API_KEY env)", type='password')
    top_k = st.slider("Retriever: top K documents", min_value=1, max_value=10, value=4)
    if st.button("Rebuild chat index (may take time)"):
        with st.spinner("Loading data and building index..."):
            dfs = load_all_data()
            info = chatbot.build_index_from_dataframes(dfs, persist=True)
        st.success(f"Index built: {info.get('n_docs', 0)} documents")

if 'history' not in st.session_state:
    st.session_state.history = []  # list of (question, answer, sources)

col1, col2 = st.columns([4,1])
with col1:
    user_q = st.text_input("Ask a question about the datasets and dashboard:")
with col2:
    if st.button("Ask"):
        # noop here; handled below with user_q
        pass

if user_q:
    key = api_key_input or os.environ.get('GOOGLE_API_KEY')
    if not key:
        st.warning("No Google API key provided. Showing top-matching rows as a fallback (no LLM call).")
        with st.spinner("Retrieving local context..."):
            docs = chatbot.get_top_docs(user_q, top_k=top_k)
            # Build a simple fallback answer summarizing the retrieved snippets
            if docs:
                snippets = []
                for s in docs:
                    meta = s.get('meta', {})
                    snippets.append(f"[{meta.get('source')}:{meta.get('row_index')}] {s.get('text')}")
                fallback_answer = "Top matching rows:\n\n" + "\n\n".join(snippets)
            else:
                fallback_answer = "No matching rows found in the local index. Please rebuild the index or provide an API key to call the LLM."
            res = {'answer': fallback_answer, 'sources': docs}
            st.session_state.history.append((user_q, res['answer'], res.get('sources', [])))
    else:
        with st.spinner("Retrieving context and asking the model..."):
            res = chatbot.answer_query(user_q, top_k=top_k, api_key=key)
            st.session_state.history.append((user_q, res['answer'], res.get('sources', [])))

st.markdown("---")
st.header("Conversation")
for q, a, sources in reversed(st.session_state.history):
    st.markdown(f"**Q:** {q}")
    st.markdown(f"**A:** {a}")
    if sources:
        with st.expander("Sources / Context snippets"):
            for s in sources:
                meta = s.get('meta', {})
                st.write(f"- {meta.get('source')} row {meta.get('row_index')} (score={s.get('score'):.3f})")
                st.write(s.get('text'))
    st.markdown('---')

st.info("Tip: Use the sidebar to rebuild the index after you update data. The first build may take some time.")
