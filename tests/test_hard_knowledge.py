import hashlib, json, re, unicodedata
from pathlib import Path
from benchmarks.hard_cases import cases
from beru.knowledge import connect

ROOT = Path(__file__).resolve().parents[1]


def normalize(s):
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"\[\d+(?:\.\d+)?s\]", "", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(re.findall(r"\w+", s))


def test_frozen_hard_set_has_40_distinct_valid_source_anchors():
    assert len(cases()) == 40 and len({c["id"] for c in cases()}) == 40
    for c in cases():
        assert 0 <= c["gold"] < len(c["options"])
        paths = [
            p
            for p in (ROOT / "knowledge").rglob("*.md")
            if c["source"] in p.stem and ".draft." not in p.name
        ]
        assert paths, c["id"]
        assert any(normalize(c["anchor"]) in normalize(p.read_text()) for p in paths), (
            c["id"]
        )


def test_new_figure_facts_are_in_the_primary_index():
    c = connect()
    for text in [
        "Clan culture",
        "Adhocracy culture",
        "corporate social responsibility",
        "Type Z",
        "read between the lines",
    ]:
        n = c.execute(
            "SELECT count(*) FROM passages WHERE source IN (?,?) AND lower(text) LIKE ?",
            (
                "knowledge/documents/DOC Support 5-1.md",
                "knowledge/documents/DOC Support 3-2.md",
                "%" + text.lower() + "%",
            ),
        ).fetchone()[0]
        assert n > 0, text
    c.close()


def test_registry_matches_current_source_files_and_covers_requested_resources():
    registry = json.loads((ROOT / "knowledge/sources.json").read_text())
    for source in registry["sources"]:
        assert (
            hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest()
            == source["sha256"]
        )
    missing = [
        r["requested"]
        for r in registry["requested_resources"]
        if r["status"] == "missing"
    ]
    assert missing == []


def test_managerial_scenarios_have_verified_primary_source_anchors():
    from benchmarks.managerial_audit import cases as managerial_cases
    text = (ROOT / 'knowledge/documents/DOC Support 6-1.md').read_text()
    assert len(managerial_cases()) == 12
    for case in managerial_cases():
        assert normalize(case['anchor']) in normalize(text)
        assert case['gold'] in range(len(case['options']))
