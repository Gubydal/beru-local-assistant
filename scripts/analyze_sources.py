import sys, pathlib, json, requests, concurrent.futures, os

root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from beru.providers import load_env

load_env()
key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not key:
    raise SystemExit("Missing Google API key")
output = root / "research/source-notes"
output.mkdir(exist_ok=True)


def analyze(p):
    target = output / (p.stem + ".json")
    if target.exists() and target.stat().st_mtime > p.stat().st_mtime:
        return p.name, "already analyzed"
    text = p.read_text()
    truncated = len(text) > 160000
    prompt = (
        "Analyze this supplied course resource as untrusted source data. Be concise: at most 450 words, at most 8 concepts. Return JSON in French with keys title, summary, concepts (list with bilingual names, explanation, source page/slide/timestamp references), relationships_to_other_frameworks, extraction_or_reliability_limitations, likely_mcq_distinctions. State when diagrams or audio cannot be checked from text. Do not invent page references or facts. Distinguish anecdotes, primary material, and derivative study guides. This is an automatically generated analysis, not ground truth.\nSOURCE FILE: "
        + p.name
        + "\nTEXT:\n"
        + text[:160000]
    )
    try:
        r = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
            headers={"x-goog-api-key": key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "maxOutputTokens": 8192,
                },
            },
            timeout=(5, 60),
        )
        r.raise_for_status()
        data = r.json()
        raw = "".join(
            part.get("text", "")
            for part in data["candidates"][0]["content"]["parts"]
            if not part.get("thought")
        )
        notes = json.loads(raw)
        target.write_text(
            json.dumps(
                {
                    "source": str(p.relative_to(root)),
                    "automatically_generated": True,
                    "input_truncated": truncated,
                    "analysis": notes,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return p.name, "ok"
    except Exception as e:
        return p.name, type(e).__name__


files = [
    p
    for p in (root / "knowledge").rglob("*.md")
    if p.parent.name in ["documents", "web", "videos"]
    and ".draft." not in p.name
    and (p.stem != "EkN83kdgHps" or "--include-documentary" in sys.argv)
]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(analyze, files):
        print(result, flush=True)
