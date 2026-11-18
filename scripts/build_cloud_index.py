"""Embed source passages once; document text is sent to the configured Google API."""

import sys, pathlib, sqlite3, os
import numpy as np
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from beru.providers import load_env
from beru.corpus import digest
from beru.cloud_retrieval import MODEL

load_env()
key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not key:
    raise SystemExit("Missing Google API key")
c = sqlite3.connect(ROOT / "knowledge/index.sqlite")
rows = c.execute("SELECT rowid,text FROM passages").fetchall()
c.close()
vectors = []
for offset in range(0, len(rows), 64):
    batch = rows[offset : offset + 64]
    body = {
        "requests": [
            {
                "model": MODEL,
                "content": {"parts": [{"text": text}]},
                "taskType": "RETRIEVAL_DOCUMENT",
                "outputDimensionality": 768,
            }
            for id, text in batch
        ]
    }
    r = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/"
        + MODEL
        + ":batchEmbedContents",
        headers={"x-goog-api-key": key},
        json=body,
        timeout=(5, 30),
    )
    r.raise_for_status()
    data = r.json()["embeddings"]
    if len(data) != len(batch):
        raise ValueError("Embedding count does not match corpus")
    vectors.extend(d["values"] for d in data)
    print("Embedded", min(offset + 64, len(rows)), "/", len(rows), flush=True)
v = np.asarray(vectors, dtype=np.float32)
v /= np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)
if not np.isfinite(v).all():
    raise ValueError("Nonfinite embedding values")
path = ROOT / "knowledge/gemini-vectors.npz"
tmp = path.with_suffix(".tmp.npz")
np.savez_compressed(
    tmp,
    ids=np.array([r[0] for r in rows]),
    vectors=v,
    corpus_hash=digest(rows),
    model=MODEL,
)
tmp.replace(path)
print("Saved local cloud-embedding index:", len(rows), "passages", flush=True)
