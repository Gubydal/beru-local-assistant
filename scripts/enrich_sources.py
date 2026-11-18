from pathlib import Path
import requests, re, concurrent.futures

root = Path(__file__).resolve().parents[1]
for name, title, url in [
    (
        "hofstede-lectures",
        "Hofstede: online lectures",
        "https://geerthofstede.com/training-consulting/online-lectures/",
    ),
    (
        "learnlight",
        "Les sept dimensions culturelles de Trompenaars",
        "https://www.learnlight.com/fr/articles/7-dimensions-culturelles-international/",
    ),
]:
    p = root / "knowledge/web" / f"{name}.md"
    text = p.read_text()
    if not text.startswith("# "):
        p.write_text(f"# {title}\n\nSource: {url}\n\n" + text)


def enrich(p):
    id = p.stem
    if len(id) != 11 or id == "VID_Valeurs":
        return
    try:
        r = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": "https://www.youtube.com/watch?v=" + id, "format": "json"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        text = p.read_text()
        text = re.sub(r"^# .*", "# " + data["title"], text, count=1)
        if text != p.read_text():
            p.write_text(text)
        return id, data["title"]
    except Exception as e:
        return id, type(e).__name__


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(enrich, (root / "knowledge/videos").glob("*.md")):
        if result:
            print(result, flush=True)
