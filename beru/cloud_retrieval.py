"""Optional multilingual query embeddings with local vectors and bounded fallback."""

import os, sqlite3, threading, pathlib
import numpy as np
import requests
from beru.corpus import digest

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL = "models/gemini-embedding-001"
_lock = threading.Lock()
_state = None
_cache = {}


def _index():
    global _state
    path = ROOT / "knowledge/gemini-vectors.npz"
    if not path.exists():
        return None
    stamp = (
        path.stat().st_mtime_ns,
        (ROOT / "knowledge/index.sqlite").stat().st_mtime_ns,
    )
    with _lock:
        if _state is not None and _state["stamp"] == stamp:
            return _state
        with np.load(path, allow_pickle=False) as data:
            c = sqlite3.connect(ROOT / "knowledge/index.sqlite")
            rows = c.execute("SELECT rowid,text FROM passages").fetchall()
            c.close()
            if str(data["corpus_hash"]) != digest(rows) or str(data["model"]) != MODEL:
                return None
            _state = {"stamp": stamp, "vectors": data["vectors"], "ids": data["ids"]}
            _cache.clear()
            return _state


def search(query, limit=24):
    if os.getenv("BERU_CLOUD_RETRIEVAL", "1") == "0":
        return []
    try:
        index = _index()
        if index is None:
            return []
        from beru.providers import load_env

        load_env()
        key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not key:
            return []
        with _lock:
            cached = _cache.get(query)
        if cached is None:
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/"
                + MODEL
                + ":embedContent",
                headers={"x-goog-api-key": key},
                json={
                    "model": MODEL,
                    "content": {"parts": [{"text": query}]},
                    "taskType": "RETRIEVAL_QUERY",
                    "outputDimensionality": 768,
                },
                timeout=(0.5, 2),
            )
            response.raise_for_status()
            vector = np.asarray(
                response.json()["embedding"]["values"], dtype=np.float32
            )
            if (
                vector.shape != (index["vectors"].shape[1],)
                or not np.isfinite(vector).all()
            ):
                return []
            vector /= max(float(np.linalg.norm(vector)), 1e-9)
            with _lock:
                if len(_cache) > 256:
                    _cache.clear()
                _cache[query] = vector
        else:
            vector = cached
        scores = index["vectors"] @ vector
        return [
            {"id": int(index["ids"][i]), "score": float(scores[i])}
            for i in np.argsort(scores)[::-1][:limit]
        ]
    except (requests.RequestException, OSError, ValueError, KeyError, sqlite3.Error):
        return []
