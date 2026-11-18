import os, sys, subprocess, pathlib

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
import numpy as np
from faster_whisper import WhisperModel

root = pathlib.Path(__file__).resolve().parents[1]
model = WhisperModel(
    sys.argv[1] if len(sys.argv) > 1 else "small", device="cpu", compute_type="int8"
)
items = [
    (
        "VID_Valeurs",
        pathlib.Path("/Users/mohammed/Downloads/New Folder With Items/VID_Valeurs.mp4"),
    )
]
for p in (root / "knowledge/media").glob("EkN83kdgHps.*"):
    if (
        p.suffix in [".webm", ".mp4", ".m4a"]
        and not pathlib.Path(str(p) + ".part").exists()
    ):
        items.append(("EkN83kdgHps", p))
        break
for name, path in items:
    audio = subprocess.check_output(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(path),
            "-f",
            "f32le",
            "-ac",
            "1",
            "-ar",
            "16000",
            "pipe:1",
        ]
    )
    segments, info = model.transcribe(
        np.frombuffer(audio, dtype=np.float32), beam_size=3, vad_filter=False
    )
    suffix = ".draft.md" if sys.argv[1:] == ["tiny"] else ".md"
    with (root / "knowledge/videos" / f"{name}{suffix}").open("w") as f:
        f.write(
            f"# {name}\n\nSource: {path}\n\nAutomatic transcription ({sys.argv[1:] or ['small']}), not manually verified.\n\n"
        )
        for segment in segments:
            f.write(f"[{segment.start:.1f}s] {segment.text}\n")
            f.flush()
    print("Completed", name, info.language, flush=True)
