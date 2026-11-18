"""Audit source provenance, extraction coverage and requested course-label mapping."""

from pathlib import Path
import json, hashlib, sqlite3

ROOT = Path(__file__).resolve().parents[1]
records = []
for folder in ["documents", "videos", "web"]:
    for p in sorted((ROOT / "knowledge" / folder).glob("*.md")):
        if ".draft." in p.name:
            continue
        text = p.read_text()
        secondary = any(s in p.stem for s in ["study_guide", "guide_complet", ".reviewed"])
        records.append(
            dict(
                id=p.stem,
                path=str(p.relative_to(ROOT)),
                kind="reviewed_question_bank"
                if ".reviewed" in p.stem
                else "secondary_summary"
                if secondary
                else "transcript"
                if folder == "videos"
                else "primary_course_or_lecture"
                if folder == "documents"
                else "web_article",
                sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                characters=len(text),
                citations="timestamps"
                if folder == "videos"
                else "pages_or_slides"
                if folder == "documents"
                else "URL",
                quality_notes=["Automatic subtitles/ASR are unverified"]
                if folder == "videos"
                else ["Figures may require visual verification"]
                if folder == "documents"
                else [],
            )
        )
mappings = [
    {
        "requested": "SUP_Managerial behavior - Cultural aspects",
        "status": "content_match",
        "path": "knowledge/documents/DOC Support 6-1.md",
    },
    {
        "requested": "CAS_Biais Culturel_Formation (Yemen)",
        "status": "content_match",
        "path": "knowledge/documents/DOC Support 6-2.md",
    },
    {
        "requested": "VID_Biais culturel de la Gestion du Temps (Maroc)",
        "status": "content_match",
        "path": "knowledge/videos/9QdyxU7tseo.md",
    },
    {
        "requested": "SUP_Organizational Culture",
        "status": "content_match",
        "path": "knowledge/documents/DOC Support 5-1.md",
    },
]
registry = {
    "sources": records,
    "requested_resources": mappings,
    "verified_diagram_pages": {
        "knowledge/documents/MIC Complet.study_guide.md": [28, 35, 41, 48, 50],
        "knowledge/documents/DOC Support 6-1.md": [1, 2, 3, 4],
        "knowledge/documents/DOC Support 3-2.md": [2, 7],
        "knowledge/documents/DOC Support 5-1.md": [3, 6, 7],
    },
    "user_supplied_table": {"source": "knowledge/documents/DOC Support 3-2.md", "section": "COI — tableau des compétences", "provenance": "User-provided slide photograph, visually transcribed; not a PDF page"},
    "notes": [
        "Course labels are matched by content; missing files must not be treated as covered.",
        "Visually checked diagram transcriptions are in the original source Markdown, not independent corroborating documents.",
        "Generated source notes are stored outside the retrieval corpus.",
    ],
}
(ROOT / "knowledge/sources.json").write_text(
    json.dumps(registry, ensure_ascii=False, indent=2)
)
c = sqlite3.connect(ROOT / "knowledge/index.sqlite")
indexed = dict(
    c.execute("SELECT source,count(*) FROM passages GROUP BY source").fetchall()
)
c.close()
stale_notes = []
for record in records:
    source = ROOT / record["path"]
    notes = ROOT / "research/source-notes" / (source.stem + ".json")
    if notes.exists() and notes.stat().st_mtime < source.stat().st_mtime:
        stale_notes.append(record["path"])
audit = {
    "sources": len(records),
    "stale_generated_notes_not_used_for_retrieval": stale_notes,
    "requested_resources": mappings,
    "verified_diagram_pages": {
        "knowledge/documents/MIC Complet.study_guide.md": [28, 35, 41, 48, 50],
        "knowledge/documents/DOC Support 6-1.md": [1, 2, 3, 4],
        "knowledge/documents/DOC Support 3-2.md": [2, 7],
        "knowledge/documents/DOC Support 5-1.md": [3, 6, 7],
    },
    "not_indexed": [r["path"] for r in records if not indexed.get(r["path"])],
    "unexpected_indexed": [p for p in indexed if p not in {r["path"] for r in records}],
    "counts": indexed,
    "transcript_warning": "jWAJFqJLWSg contains visibly garbled automatic transcription in mixed English/Darija sections; the clear English portions cannot validate all oral course terminology.",
}
(ROOT / "research/hard-audit/knowledge-audit.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2)
)
print(
    json.dumps(
        {k: v for k, v in audit.items() if k != "counts"}, ensure_ascii=False, indent=2
    )
)
