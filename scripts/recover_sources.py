import pathlib, json, subprocess, re
from youtube_transcript_api import YouTubeTranscriptApi

ROOT = pathlib.Path(__file__).resolve().parents[1]


def recover_pdf(item):
    if item.get("empty_pages"):
        p = subprocess.run(
            [str(ROOT / "bin/beru-ocr"), item["source"]], capture_output=True, text=True
        )
        if p.returncode == 0:
            (ROOT / item["output"]).write_text(
                "# "
                + pathlib.Path(item["source"]).stem
                + "\n\nOriginal: "
                + item["source"]
                + "\n\n"
                + p.stdout
            )
        return item["source"], p.returncode


manifest = json.loads((ROOT / "knowledge/manifest.json").read_text())
for item in manifest:
    if item.get("empty_pages"):
        print(recover_pdf(item), flush=True)
text = (ROOT / "knowledge/web/hofstede-lectures.md").read_text()
for id in dict.fromkeys(re.findall(r"watch\?v=([\w-]+)", text)):
    try:
        t = YouTubeTranscriptApi().fetch(id, languages=["en", "fr"])
        (ROOT / "knowledge/videos" / f"{id}.md").write_text(
            f"# Hofstede lecture {id}\n\nSource: https://www.youtube.com/watch?v={id}\n\n"
            + "\n".join(f"[{s.start:.1f}s] {s.text}" for s in t)
        )
        print("transcript", id, flush=True)
    except Exception as e:
        print("unavailable", id, str(e)[:150], flush=True)
