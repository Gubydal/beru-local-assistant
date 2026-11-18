import json, tempfile, subprocess
from pathlib import Path
from PIL import ImageOps, ImageFilter
from beru.knowledge import ROOT
from beru.question import parse


def _read(image):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "capture.png"
        image.save(path)
        output = subprocess.check_output(
            [str(ROOT / "bin/beru-ocr"), str(path), "--json"], text=True, timeout=10
        )
    return parse(json.loads(output)["lines"])


def read(image):
    try:
        return _read(image)
    except ValueError as first:
        # One bounded local retry, never ask an LLM to guess missing choices.
        cleaned = ImageOps.autocontrast(
            image.convert("L").filter(ImageFilter.MedianFilter(3))
        )
        if cleaned.width < 1800:
            cleaned = cleaned.resize((cleaned.width * 2, cleaned.height * 2))
        try:
            return _read(cleaned)
        except ValueError:
            raise first
