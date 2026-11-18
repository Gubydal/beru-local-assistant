"""Optional local multilingual vector retrieval; JSON stdin/stdout worker."""

import json, sys, pathlib, os, numpy as np

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
if len(sys.argv) > 1 and sys.argv[1] == "search":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
from model2vec import StaticModel

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from beru.corpus import digest

model = StaticModel.from_pretrained(
    "minishlab/potion-multilingual-128M", force_download=False
)
index = root / "knowledge/semantic.npz"
if sys.argv[1] == "index":
    import sqlite3

    c = sqlite3.connect(root / "knowledge/index.sqlite")
    rows = c.execute("SELECT rowid,text FROM passages").fetchall()
    vectors = model.encode([r[1] for r in rows])
    vectors = vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-9)
    np.savez_compressed(
        index,
        ids=np.array([r[0] for r in rows]),
        vectors=vectors,
        corpus_hash=digest(rows),
    )
    print(len(rows))
else:
    data = np.load(index)
    import sqlite3

    c = sqlite3.connect(root / "knowledge/index.sqlite")
    rows = c.execute("SELECT rowid,text FROM passages").fetchall()
    c.close()
    if "corpus_hash" not in data or str(data["corpus_hash"]) != digest(rows):
        print(json.dumps({"ready": False, "error": "stale vector index"}), flush=True)
        sys.exit(1)
    vectors = data["vectors"]
    ids = data["ids"]
    print(json.dumps({"ready": True}), flush=True)
    for line in sys.stdin:
        q = model.encode([json.loads(line)["query"]])[0]
        q = q / max(np.linalg.norm(q), 1e-9)
        scores = vectors @ q
        order = np.argsort(scores)[::-1][:24]
        print(
            json.dumps(
                {
                    "hits": [
                        {"id": int(ids[i]), "score": float(scores[i])} for i in order
                    ]
                }
            ),
            flush=True,
        )
