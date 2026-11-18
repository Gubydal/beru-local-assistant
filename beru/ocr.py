import json, tempfile, subprocess
from pathlib import Path
from PIL import ImageOps, ImageFilter
from beru.knowledge import ROOT
from beru.question import parse, parse_written


def _read(image, mode="mcq"):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "capture.png"
        image.save(path)
        output = subprocess.check_output(
            [str(ROOT / "bin/beru-ocr"), str(path), "--json"], text=True, timeout=10
        )
    return (parse_written if mode == "written" else parse)(json.loads(output)["lines"])


def read(image, mode="mcq"):
    try:
        return _read(image) if mode == "mcq" else _read(image, mode)
    except ValueError as first:
        # One bounded local retry, never ask an LLM to guess missing choices.
        cleaned = ImageOps.autocontrast(
            image.convert("L").filter(ImageFilter.MedianFilter(3))
        )
        if cleaned.width < 1800:
            cleaned = cleaned.resize((cleaned.width * 2, cleaned.height * 2))
        try:
            return _read(cleaned) if mode == "mcq" else _read(cleaned, mode)
        except ValueError:
            raise first
