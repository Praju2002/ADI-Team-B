"""
Simple retrieval + Google Generative API chat glue.

This module implements a lightweight TF-IDF-based retriever over DataFrame rows
and a small wrapper to call Google's Generative API (Text-Bison) using an API key.

Design choices:
- Uses scikit-learn TfidfVectorizer for retrieval (no heavy vector DB dependency).
- Persists index (vectorizer, docs, matrix) under Raw_Data/processed/chat_index/.
- Calls the Generative API via REST using the API key (set in env var GOOGLE_API_KEY).

Note: For production or larger datasets, replace retriever with an embeddings+vector DB (Chroma/FAISS)
and use the Vertex AI client libraries instead of raw REST calls.
"""
from __future__ import annotations

import os
import time
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import scipy.sparse as sps
import pandas as pd
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

INDEX_DIR = Path('Raw_Data/processed/chat_index')
INDEX_DIR.mkdir(parents=True, exist_ok=True)
_DOCS_PKL = INDEX_DIR / 'docs.pkl'
_VECT_PKL = INDEX_DIR / 'vectorizer.pkl'
_MAT_NPZ = INDEX_DIR / 'matrix.npz'


def _row_to_text(df: pd.DataFrame, idx: int) -> str:
    """Convert a DataFrame row into a compact text representation."""
    row = df.iloc[idx]
    parts = []
    for c in df.columns:
        val = row.get(c)
        if pd.isna(val):
            continue
        try:
            parts.append(f"{c}: {val}")
        except Exception:
            parts.append(f"{c}: {str(val)}")
    return ' | '.join(parts)


def build_index_from_dataframes(dfs: Dict[str, pd.DataFrame], persist: bool = True) -> Dict[str, Any]:
    """Build TF-IDF index over dataframe rows. Returns metadata about index.

    dfs: mapping of table name -> DataFrame
    """
    docs = []  # list of {'text':..., 'meta':{...}}
    for table, df in dfs.items():
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        for i in range(len(df)):
            text = _row_to_text(df, i)
            if not text:
                continue
            docs.append({'text': text, 'meta': {'source': table, 'row_index': int(i)}})

    texts = [d['text'] for d in docs]
    if not texts:
        # write empty artifacts so callers can rely on them
        if persist:
            with open(_DOCS_PKL, 'wb') as fh:
                pickle.dump([], fh)
            with open(_VECT_PKL, 'wb') as fh:
                pickle.dump(TfidfVectorizer(), fh)
            sps.save_npz(_MAT_NPZ, sps.csr_matrix((0, 0)))
        return {'n_docs': 0}

    vect = TfidfVectorizer(max_features=20000, ngram_range=(1, 2))
    mat = vect.fit_transform(texts)

    if persist:
        with open(_DOCS_PKL, 'wb') as fh:
            pickle.dump(docs, fh)
        with open(_VECT_PKL, 'wb') as fh:
            pickle.dump(vect, fh)
        # Save sparse matrix to NPZ to avoid dense memory blowup
        sps.save_npz(_MAT_NPZ, mat.tocsr())

    return {'n_docs': len(docs)}


def load_index() -> Tuple[List[Dict[str, Any]], Optional[TfidfVectorizer], Optional[sps.spmatrix]]:
    """Load persisted index artifacts. Returns (docs, vectorizer, matrix)"""
    if not _DOCS_PKL.exists() or not _VECT_PKL.exists() or not _MAT_NPZ.exists():
        return [], None, None
    try:
        with open(_DOCS_PKL, 'rb') as fh:
            docs = pickle.load(fh)
        with open(_VECT_PKL, 'rb') as fh:
            vect = pickle.load(fh)
        mat = sps.load_npz(_MAT_NPZ)
        return docs, vect, mat
    except Exception:
        return [], None, None


def get_top_docs(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """Return top_k docs (with scores) for query using cosine similarity over TF-IDF."""
    docs, vect, mat = load_index()
    if not docs or vect is None or mat is None or mat.size == 0:
        return []

    q_vec = vect.transform([query]).toarray().astype('float32')
    # linear_kernel gives cosine for normalized tf-idf
    scores = linear_kernel(q_vec, mat)[0]
    top_idx = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in top_idx:
        results.append({'text': docs[idx]['text'], 'meta': docs[idx]['meta'], 'score': float(scores[idx])})
    return results


def _build_prompt(query: str, docs: List[Dict[str, Any]], include_graph: bool = False, table_schemas: Dict[str, List[str]] = None) -> str:
    """Compose a prompt for the LLM that includes retrieved contexts and the user query."""
    header = (
        "You are a helpful assistant that answers questions about the dataset. "
        "When you use facts from the provided context, cite the source in brackets like [table:row_index].\n"
    )
    if include_graph:
        schema_info = "\n".join([f"- {table}: {cols}" for table, cols in table_schemas.items()]) if table_schemas else "No schema available."
        header += (
            "The user has requested a visualization. You can generate a graph by writing a Python code snippet.\n"
            "Wrap the code in ```python:graph\n...\n```.\n"
            "The code MUST use `plotly.express` as `px`.\n"
            f"Assume a dictionary `dfs` is available containing dataframes. \n"
            f"Available tables and their columns:\n{schema_info}\n"
            "The code must assign the figure to a variable named `fig`.\n"
            "Do not use `fig.show()`, just create the `fig` object.\n"
            "IMPORTANT: The datasets are large. You MUST aggregate the data (e.g., using `groupby().sum()` or `mean()`) before plotting. DO NOT plot raw dataframes directly.\n"
            "Example:\n"
            "```python:graph\n"
            "df_agg = dfs['table_name'].groupby('col1')['col2'].sum().reset_index()\n"
            "fig = px.bar(df_agg, x='col1', y='col2', title='My Graph')\n"
            "```\n"
            "After the code block, provide a clear and detailed explanation of what the graph visualizes. Explain what the x and y axes represent, and highlight any key trends, outliers, or insights visible in the data.\n\n"
        )

    context_blocks = []
    for i, d in enumerate(docs, start=1):
        meta = d.get('meta', {})
        tag = f"[{meta.get('source')}:{meta.get('row_index')}]"
        context_blocks.append(f"Context {i} {tag}: {d.get('text')}")

    context_text = "\n\n".join(context_blocks)
    prompt = f"{header}CONTEXT:\n{context_text}\n\nQUESTION: {query}\n\nAnswer concisely and refer to sources where appropriate."
    return prompt


def call_google_bison(prompt: str, api_key: Optional[str] = None, max_output_tokens: int = 512, temperature: float = 0.0) -> str:
    """Call Google Generative API (text-bison) via REST using an API key.

    Expects environment variable `GOOGLE_API_KEY` or explicit api_key.
    """
    key = api_key or os.environ.get('GOOGLE_API_KEY')
    if not key:
        raise RuntimeError('Google API key not set. Provide GOOGLE_API_KEY env var or pass api_key')

    url = f"https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generate?key={key}"
    body = {
        'prompt': {'text': prompt},
        'temperature': temperature,
        'maxOutputTokens': max_output_tokens,
    }
    try:
        resp = requests.post(url, json=body, timeout=30)
        # don't raise immediately, we want to capture body on errors
        if resp.status_code >= 400:
            # return helpful debug info without leaking the key
            return f"[Generative API error: {resp.status_code} {resp.text}]"
        data = resp.json()
        # persist raw response for debugging (no API key saved)
        try:
            with open(INDEX_DIR / 'last_response.json', 'w') as fh:
                import json

                json.dump(data, fh, indent=2)
        except Exception:
            pass

        # Defensive parsing: try several common fields returned by the Generative API
        # 1) data['candidates'][0]['content']
        if isinstance(data, dict):
            cands = data.get('candidates') or data.get('candidates')
            if isinstance(cands, list) and cands:
                cand = cands[0]
                # Candidates may be dicts with 'content' or 'output' or 'text'
                for key in ('content', 'output', 'text'):
                    if isinstance(cand, dict) and key in cand:
                        return cand[key]

            # 2) data.get('output')
            if 'output' in data and isinstance(data['output'], str):
                return data['output']

            # 3) data.get('responses') -> list -> .get('content')
            resps = data.get('responses')
            if isinstance(resps, list) and resps:
                r0 = resps[0]
                if isinstance(r0, dict):
                    for key in ('content', 'output', 'text'):
                        if key in r0:
                            return r0[key]

        # fallback: stringify
        return str(data)
    except Exception as e:
        return f"[LLM call failed: {e}]"


def call_openai(prompt: str, api_key: Optional[str] = None, max_output_tokens: int = 512, temperature: float = 0.0) -> str:
    """Call OpenAI Chat Completions (gpt-3.5-turbo) using an API key.

    This uses the REST API and expects an API key starting with 'sk-'.
    """
    key = api_key or os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI_KEY')
    if not key:
        raise RuntimeError('OpenAI API key not set. Provide OPENAI_API_KEY env var or pass api_key')

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}'
    }
    body = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant that answers questions about tabular datasets. Cite sources in brackets like [table:row_index].'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': max_output_tokens,
        'temperature': temperature,
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code >= 400:
            return f"[OpenAI API error: {resp.status_code} {resp.text}]"
        data = resp.json()
        # extract text
        choices = data.get('choices')
        if isinstance(choices, list) and choices:
            first = choices[0]
            # chat completions: message -> content
            msg = first.get('message') or {}
            content = msg.get('content') or first.get('text')
            if content:
                return content
        # fallback
        return json.dumps(data)
    except Exception as e:
        return f"[OpenAI call failed: {e}]"


def call_groq(prompt: str, api_key: Optional[str] = None, max_output_tokens: int = 512, temperature: float = 0.0) -> str:
    """Call Groq API (llama3-70b-8192) using an API key.

    This uses the REST API and expects an API key starting with 'gsk_'.
    """
    key = api_key or os.environ.get('GROQ_API_KEY')
    if not key:
        raise RuntimeError('Groq API key not set. Provide GROQ_API_KEY env var or pass api_key')

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {key}'
    }
    body = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant that answers questions about tabular datasets. Cite sources in brackets like [table:row_index].'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': max_output_tokens,
        'temperature': temperature,
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code >= 400:
            return f"[Groq API error: {resp.status_code} {resp.text}]"
        data = resp.json()
        # extract text
        choices = data.get('choices')
        if isinstance(choices, list) and choices:
            first = choices[0]
            # chat completions: message -> content
            msg = first.get('message') or {}
            content = msg.get('content') or first.get('text')
            if content:
                return content
        # fallback
        return json.dumps(data)
    except Exception as e:
        return f"[Groq call failed: {e}]"


def answer_query(query: str, top_k: int = 4, api_key: Optional[str] = None, include_graph: bool = False, table_schemas: Dict[str, List[str]] = None) -> Dict[str, Any]:
    """Retrieve supporting docs and ask the LLM for an answer.

    Returns: {'answer': str, 'sources': [{'meta','score','text'}]}
    """
    docs = get_top_docs(query, top_k=top_k)
    prompt = _build_prompt(query, docs, include_graph=include_graph, table_schemas=table_schemas)
    # Choose backend by key type: OpenAI keys usually start with 'sk-', Groq keys start with 'gsk_'
    resp = None
    if api_key and str(api_key).startswith('sk-'):
        resp = call_openai(prompt, api_key=api_key)
    elif (api_key and str(api_key).startswith('gsk_')) or os.environ.get('GROQ_API_KEY'):
        # Prefer Groq if key provided or in env
        # If api_key is passed and it's not gsk, but we have GROQ_API_KEY in env, we might default to Groq?
        # The logic below: if explicit api_key is gsk, use Groq.
        # If no explicit api_key, check env for GROQ_API_KEY.
        effective_key = api_key if (api_key and str(api_key).startswith('gsk_')) else os.environ.get('GROQ_API_KEY')
        if effective_key:
             resp = call_groq(prompt, api_key=effective_key)
        else:
             # default to Google Generative API
             resp = call_google_bison(prompt, api_key=api_key)
    else:
        # default to Google Generative API
        resp = call_google_bison(prompt, api_key=api_key)
    # Also compute a deterministic insight summary from the retrieved docs so UI can show
    insight = summarize_docs_insights(docs)
    return {'answer': resp, 'sources': docs, 'insight': insight}


def _try_parse_number(s: str):
    """Try to parse a string as number. Returns number or original string."""
    if s is None:
        return None
    s = str(s).strip()
    if s == '':
        return None
    # handle percentages
    if s.endswith('%'):
        try:
            return float(s.rstrip('%').replace(',',''))
        except Exception:
            pass
    try:
        return float(s.replace(',',''))
    except Exception:
        return s


def _parse_doc_text_to_dict(text: str) -> Dict[str, Any]:
    """Parse a doc text of the form 'col: val | col2: val2' into a dict."""
    out = {}
    if not text:
        return out
    parts = [p.strip() for p in text.split('|') if p.strip()]
    for p in parts:
        if ':' not in p:
            continue
        k, v = p.split(':', 1)
        k = k.strip()
        v = v.strip()
        parsed = _try_parse_number(v)
        out[k] = parsed
    return out


def summarize_docs_insights(docs: List[Dict[str, Any]]) -> Any:
    """Create a short, human-friendly insight summary from a list of retrieved docs.

    Returns either a string (short summary) or a dict with simple aggregates.
    The summarizer is intentionally conservative: it extracts numeric columns and
    computes counts/means for the most common numeric fields, and reports top
    categorical values (e.g., country) when present.
    """
    if not docs:
        return None

    parsed_rows = [_parse_doc_text_to_dict(d.get('text', '')) for d in docs]
    # collect column types
    numeric_cols = {}
    categorical_counts = {}
    for row in parsed_rows:
        for k, v in row.items():
            if v is None:
                continue
            if isinstance(v, (int, float)):
                numeric_cols.setdefault(k, []).append(float(v))
            else:
                categorical_counts.setdefault(k, {}).setdefault(str(v), 0)
                categorical_counts[k][str(v)] += 1

    insight = {}
    # summarize numeric columns (top 4 by frequency)
    num_items = sorted(numeric_cols.items(), key=lambda kv: len(kv[1]), reverse=True)[:4]
    for k, vals in num_items:
        arr = np.array(vals)
        insight[f"avg_{k}"] = round(float(np.nanmean(arr)), 2)
        insight[f"sum_{k}"] = float(np.nansum(arr))
        insight[f"min_{k}"] = float(np.nanmin(arr))
        insight[f"max_{k}"] = float(np.nanmax(arr))

    # summarize categorical columns: top value
    for k, counts in categorical_counts.items():
        top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[0]
        insight[f"top_{k}"] = {"value": top[0], "count": int(top[1])}

    # Return a dict for UI to render succinctly
    return insight if insight else None
