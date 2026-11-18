import sqlite3, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DB = ROOT / "knowledge/index.sqlite"


def connect():
    c = sqlite3.connect(DB)
    c.execute(
        'CREATE VIRTUAL TABLE IF NOT EXISTS passages USING fts5(source UNINDEXED, section UNINDEXED, text, tokenize="unicode61 remove_diacritics 2")'
    )
    return c


def index():
    (ROOT / "knowledge/semantic.npz").unlink(missing_ok=True)
    (ROOT / "knowledge/gemini-vectors.npz").unlink(missing_ok=True)
    c = connect()
    c.execute("DELETE FROM passages")
    count = 0
    for p in (ROOT / "knowledge").rglob("*.md"):
        if (
            p.name in ["READINESS.md", "CATALOG.md", "CONCEPTS.md"]
            or ".draft." in p.name
        ):
            continue
        text = p.read_text()
        section = p.stem
        for block in re.split(r"(?m)^(?=## )", text):
            lines = block.splitlines()
            if lines and lines[0].startswith("## "):
                section = lines[0][3:]
            # overlapping chunks retain raw evidence and source identity
            block = re.sub(r"(\w)-\n(\w)", r"\1\2", block)
            words = block.split()
            for start in range(0, len(words), 240):
                chunk = " ".join(words[start : start + 320])
                if len(chunk) < 15:
                    continue
                c.execute(
                    "INSERT INTO passages VALUES (?,?,?)",
                    (str(p.relative_to(ROOT)), section, chunk),
                )
                count += 1
    c.commit()
    c.close()
    return count


def keyword_search(question, limit=8):
    stop = set(
        "the and for that this with which what who how does are was were from into not can all une des les dans pour quelle quel quels quelles est sont qui que quoi comment avec sur par aux ces cette cet selon concerne dimension dimensions parmi suivantes suivant following answer option correct question choose select".split()
    )
    tokens = [
        t
        for t in dict.fromkeys(re.findall(r"[^\W_]{3,}", question.lower()))
        if t not in stop
    ][:60]
    if not tokens:
        return []
    query = " OR ".join('"' + t + '"' for t in tokens)
    c = connect()
    rows = c.execute(
        "SELECT source,section,text,bm25(passages) FROM passages WHERE passages MATCH ? ORDER BY bm25(passages) LIMIT ?",
        (query, limit),
    ).fetchall()
    c.close()
    return [dict(source=r[0], section=r[1], text=r[2], score=r[3]) for r in rows]


def search(question, limit=8):
    from beru import semantic, cloud_retrieval

    cloud_hits = cloud_retrieval.search(question)
    keyword = keyword_search(question, 24)
    semantic_hits = semantic.search(question)
    if not semantic_hits and not cloud_hits:
        return sorted(
            keyword,
            key=lambda e: (
                e["score"]
                * (
                    0.45
                    if any(n in e["source"] for n in ["study_guide", "guide_complet", ".reviewed."])
                    else 1
                )
            ),
        )[:limit]
    c = connect()
    ranks = {}
    passages = {}
    for rank, e in enumerate(keyword):
        key = (e["source"], e["section"], e["text"])
        ranks[key] = (0.05 if cloud_hits else 1) / (60 + rank + 1)
        passages[key] = e
    for rank, hit in enumerate(semantic_hits):
        row = c.execute(
            "SELECT source,section,text FROM passages WHERE rowid=?", (hit["id"],)
        ).fetchone()
        if not row:
            continue
        key = tuple(row)
        ranks[key] = ranks.get(key, 0) + (0.05 if cloud_hits else 1) / (60 + rank + 1)
        passages[key] = dict(
            source=row[0], section=row[1], text=row[2], score=hit["score"]
        )
    for rank, hit in enumerate(cloud_hits):
        row = c.execute(
            "SELECT source,section,text FROM passages WHERE rowid=?", (hit["id"],)
        ).fetchone()
        if not row:
            continue
        key = tuple(row)
        ranks[key] = ranks.get(key, 0) + 1 / (60 + rank + 1)
        passages[key] = dict(
            source=row[0],
            section=row[1],
            text=row[2],
            score=hit["score"],
            retrieval_mode="cloud_hybrid",
        )
    c.close()
    return [
        passages[k]
        for k in sorted(
            ranks,
            key=lambda k: (
                ranks[k]
                * (
                    0.45
                    if any(n in k[0] for n in ["study_guide", "guide_complet", ".reviewed."])
                    else 1
                )
            ),
            reverse=True,
        )[:limit]
    ]


if __name__ == "__main__":
    print(f"Indexed {index()} passages")
