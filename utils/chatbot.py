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


def _build_prompt(query: str, docs: List[Dict[str, Any]]) -> str:
    """Compose a prompt for the LLM that includes retrieved contexts and the user query."""
    header = (
        "You are a helpful assistant that answers questions about the dataset. "
        "When you use facts from the provided context, cite the source in brackets like [table:row_index].\n\n"
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
        resp.raise_for_status()
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


def answer_query(query: str, top_k: int = 4, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve supporting docs and ask the LLM for an answer.

    Returns: {'answer': str, 'sources': [{'meta','score','text'}]}
    """
    docs = get_top_docs(query, top_k=top_k)
    prompt = _build_prompt(query, docs)
    resp = call_google_bison(prompt, api_key=api_key)
    return {'answer': resp, 'sources': docs}
