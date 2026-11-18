import concurrent.futures, json, pathlib
from pypdf import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi

root = pathlib.Path(__file__).resolve().parents[1]
records = []
for path in pathlib.Path("/Users/mohammed/Downloads/New Folder With Items").glob(
    "*.pdf"
):
    try:
        reader = PdfReader(path)
        pages = [p.extract_text() or "" for p in reader.pages]
        target = root / "knowledge/documents" / f"{path.stem}.md"
        target.write_text(
            f"# {path.stem}\n\nOriginal: {path}\n\n"
            + "\n\n".join(f"## Page {i + 1}\n\n{text}" for i, text in enumerate(pages))
        )
        records.append(
            {
                "source": str(path),
                "output": str(target.relative_to(root)),
                "pages": len(pages),
                "characters": sum(map(len, pages)),
                "empty_pages": [i + 1 for i, t in enumerate(pages) if not t.strip()],
            }
        )
    except Exception as e:
        records.append({"source": str(path), "error": str(e)})
ids = [
    "9QdyxU7tseo",
    "NFVMhfifZco",
    "jWAJFqJLWSg",
    "eUsU2qf1zqA",
    "z5EEz_R_RiE",
    "EkN83kdgHps",
    "7reXpmEc0Jo",
]


def video(id):
    try:
        transcript = YouTubeTranscriptApi().fetch(id, languages=["fr", "en"])
        target = root / "knowledge/videos" / f"{id}.md"
        target.write_text(
            f"# Video {id}\n\nSource: https://www.youtube.com/watch?v={id}\n\n"
            + "\n".join(f"[{s.start:.1f}s] {s.text}" for s in transcript)
        )
        return {
            "source": f"https://www.youtube.com/watch?v={id}",
            "output": str(target.relative_to(root)),
        }
    except Exception as e:
        return {"source": f"https://www.youtube.com/watch?v={id}", "error": str(e)}


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    records.extend(pool.map(video, ids))
(root / "knowledge/manifest.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2)
)
print(json.dumps(records, ensure_ascii=False, indent=2))
