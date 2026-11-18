from pathlib import Path
import subprocess, os

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
media = ROOT / "knowledge/media"
media.mkdir(exist_ok=True)
items = [
    (
        "VID_Valeurs",
        Path("/Users/mohammed/Downloads/New Folder With Items/VID_Valeurs.mp4"),
    )
]
try:
    subprocess.run(
        [
            str(ROOT / ".media-venv/bin/yt-dlp"),
            "-f",
            "bestaudio/best",
            "--no-playlist",
            "-o",
            str(media / "EkN83kdgHps.%(ext)s"),
            "https://www.youtube.com/watch?v=EkN83kdgHps",
        ],
        check=True,
        timeout=900,
    )
    items.append(
        (
            "EkN83kdgHps",
            next(
                p
                for p in media.glob("EkN83kdgHps.*")
                if p.suffix in [".webm", ".mp4", ".m4a"]
            ),
        )
    )
except Exception as e:
    print("Video download unavailable:", str(e), flush=True)
model = WhisperModel("small", device="cpu", compute_type="int8")
for name, path in items:
    segments, info = model.transcribe(str(path), beam_size=3, vad_filter=True)
    target = ROOT / "knowledge/videos" / f"{name}.md"
    with target.open("w") as f:
        f.write(
            f"# {name}\n\nSource: {path if name == 'VID_Valeurs' else 'https://www.youtube.com/watch?v=' + name}\n\nAutomatic speech recognition; unverified.\n\n"
        )
        for s in segments:
            f.write(f"[{s.start:.1f}s] {s.text.strip()}\n")
            f.flush()
    print("Transcribed", name, info.language, flush=True)
