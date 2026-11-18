"""Local integration checks use real Apple Vision; no cloud calls or screen access."""

from unittest.mock import patch
import pytest
from PIL import Image
from benchmarks.cases import dataset
from benchmarks.render import render
from beru.ocr import read
from beru import knowledge


@pytest.mark.parametrize("variant", ["clean", "question_only", "tiny", "blur"])
def test_real_apple_vision_preserves_critical_option_words(variant):
    q = read(render(dataset()[2], variant))
    assert "MOINS" in q.options["a"] and "PLUS" in q.options["b"]
    assert q.box and 0 <= q.box[0] < q.box[2] <= 1


def test_real_ocr_blank_rejected_after_bounded_retry():
    with pytest.raises(ValueError):
        read(Image.new("RGB", (820, 290), "white"))


def test_index_preserves_provenance_excludes_notes_and_dehyphenates(tmp_path):
    folder = tmp_path / "knowledge"
    folder.mkdir()
    (folder / "documents").mkdir()
    (folder / "documents/course.md").write_text(
        "# Course\n## Page 7\nCulture trans-\nmise socialement. " * 20
    )
    (folder / "READINESS.md").write_text("Should never become evidence " * 30)
    (folder / "foo.draft.md").write_text("Draft source " * 30)
    (folder / "semantic.npz").write_bytes(b"old")
    with (
        patch.object(knowledge, "ROOT", tmp_path),
        patch.object(knowledge, "DB", folder / "index.sqlite"),
    ):
        n = knowledge.index()
        assert n > 0 and not (folder / "semantic.npz").exists()
        rows = knowledge.keyword_search("transmise")
        assert rows and rows[0]["section"] == "Page 7"
        assert all("draft" not in r["source"] for r in rows)
        assert knowledge.index() == n


def test_hybrid_ranks_original_source_over_derivative_summary(tmp_path):
    with patch.object(knowledge, "DB", tmp_path / "test.sqlite"):
        c = knowledge.connect()
        c.executemany(
            "INSERT INTO passages VALUES (?,?,?)",
            [
                (
                    "course.md",
                    "Page 1",
                    "Power distance means acceptance of unequal power.",
                ),
                (
                    "study_guide.md",
                    "Page 2",
                    "Power distance means acceptance of unequal power.",
                ),
            ],
        )
        c.commit()
        c.close()
        with patch(
            "beru.semantic.search",
            return_value=[{"id": 2, "score": 0.9}, {"id": 1, "score": 0.8}],
        ):
            hits = knowledge.search("power distance")
            assert hits[0]["source"] == "course.md"


def test_stale_vector_ids_cannot_invent_evidence(tmp_path):
    with patch.object(knowledge, "DB", tmp_path / "test.sqlite"):
        c = knowledge.connect()
        c.execute(
            "INSERT INTO passages VALUES (?,?,?)",
            ("course.md", "Page 1", "Culture is learned and shared."),
        )
        c.commit()
        c.close()
        with patch("beru.semantic.search", return_value=[{"id": 999, "score": 0.99}]):
            hits = knowledge.search("culture")
            assert hits[0]["source"] == "course.md"
