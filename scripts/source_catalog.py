from pathlib import Path
import json, re

root = Path(__file__).resolve().parents[1]
rows = []
for p in sorted((root / "knowledge").rglob("*.md")):
    if p.name in ["READINESS.md", "CATALOG.md", "CONCEPTS.md"] or ".draft." in p.name:
        continue
    text = p.read_text()
    rows.append(
        {
            "file": str(p.relative_to(root)),
            "characters": len(text),
            "pages_or_slides": len(re.findall(r"^## (?:Page|Slide) ", text, re.M)),
            "timestamped_lines": len(re.findall(r"^\[\d", text, re.M)),
            "secondary": any(marker in p.stem for marker in ["study_guide", "guide_complet", ".reviewed"]),
        }
    )
(root / "knowledge/catalog.json").write_text(
    json.dumps(rows, ensure_ascii=False, indent=2)
)
print("Sources:", len(rows), "Characters:", sum(r["characters"] for r in rows))
