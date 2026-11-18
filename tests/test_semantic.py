from unittest.mock import patch, Mock
from beru import semantic
import queue


def test_missing_embedding_worker_falls_back_without_background_exception(tmp_path):
    with patch.object(semantic, "ROOT", tmp_path):
        (tmp_path / "knowledge").mkdir()
        (tmp_path / "knowledge/semantic.npz").write_bytes(b"bad")
        s = semantic.Semantic()
        s.start()
        assert not s.ready


def test_unresponsive_worker_is_disabled_and_keyword_search_can_continue():
    s = semantic.Semantic.__new__(semantic.Semantic)
    s.ready = True
    s.process = Mock()
    s.responses = Mock()
    s.responses.get.side_effect = queue.Empty
    s.lock = __import__("threading").Lock()
    assert s.search("Question") == [] and not s.ready


def test_corpus_identity_changes_with_text_and_row_ids():
    from beru.corpus import digest

    assert digest([(1, "MOINS")]) != digest([(1, "PLUS")])
    assert digest([(1, "MOINS")]) != digest([(2, "MOINS")])
    assert digest([(1, "MOINS")]) == digest([(1, "MOINS")])
