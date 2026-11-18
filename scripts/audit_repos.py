from pathlib import Path
import subprocess, json

root = Path(__file__).resolve().parents[1]
rows = []
for p in sorted((root / "research/repos").iterdir()):
    if not p.is_dir():
        continue
    commit = subprocess.check_output(
        ["git", "-C", str(p), "rev-parse", "HEAD"], text=True
    ).strip()
    files = list(p.rglob("*"))
    source = [
        str(f.relative_to(p))
        for f in files
        if f.is_file()
        and ".git" not in f.parts
        and f.suffix in [".py", ".js", ".ts", ".tsx", ".rs"]
    ]
    rows.append(
        {
            "repository": p.name,
            "commit": commit,
            "source_files": len(source),
            "license_present": (p / "LICENSE").exists(),
            "entrypoints": source[:20],
        }
    )
(root / "research/repository-inventory.json").write_text(json.dumps(rows, indent=2))
