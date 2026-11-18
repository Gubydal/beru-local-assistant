from pathlib import Path
import re, requests, concurrent.futures
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
urls = re.findall(
    r"https://[^\s)]+\.pptx", (ROOT / "knowledge/web/hofstede-lectures.md").read_text()
)
folder = ROOT / "knowledge/media"
folder.mkdir(exist_ok=True)


def extract(url):
    try:
        data = requests.get(url, timeout=30)
        data.raise_for_status()
        path = folder / url.split("/")[-1]
        path.write_bytes(data.content)
        p = Presentation(path)
        text = "# " + path.stem + "\n\nSource: " + url + "\n\n"
        for i, slide in enumerate(p.slides):
            text += (
                f"## Slide {i + 1}\n\n"
                + "\n".join(
                    shape.text for shape in slide.shapes if shape.has_text_frame
                )
                + "\n\n"
            )
        (ROOT / "knowledge/documents" / f"{path.stem}.md").write_text(text)
        return path.name, "ok"
    except Exception as e:
        return url, str(e)


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for r in pool.map(extract, urls):
        print(r, flush=True)
