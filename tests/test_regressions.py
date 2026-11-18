import concurrent.futures, time
from unittest.mock import patch
import pytest
from PIL import Image
from beru.app import App
from benchmarks.cases import dataset
from benchmarks.render import render


def make_app(qtbot):
    app = App()
    app.timer.stop()
    qtbot.addWidget(app)
    return app


def test_new_question_differs_by_one_word(qtbot):
    app = make_app(qtbot)
    case = dataset()[2]
    before = render(case, "question_only")
    changed = dict(case)
    changed["stem"] = case["stem"].replace("Hofstede", "HOFSTEDE")
    after = render(changed, "question_only")
    app.region = {"left": 0, "top": 0, "width": 820, "height": 290}
    app.running = True
    with patch.object(app, "capture_image", return_value=before):
        app.tick()
    generation = app.generation
    with patch.object(app, "capture_image", return_value=after):
        app.tick()
    assert app.generation > generation


def test_pause_discards_pending(qtbot):
    app = make_app(qtbot)
    app.running = True
    app.pending = (1, Image.new("RGB", (10, 10)), "gemini", time.monotonic(), False)
    app.toggle()
    assert app.pending is None


def test_manual_capture_handles_permission_error(qtbot):
    app = make_app(qtbot)
    app.region = {"left": 0, "top": 0, "width": 10, "height": 10}
    with patch.object(
        app, "capture_image", side_effect=PermissionError("Screen Recording disabled")
    ):
        app.capture()
    assert "Screen" in app.status.text()


def test_stale_answer_never_displayed(qtbot):
    app = make_app(qtbot)
    app.generation = 2
    app.future = concurrent.futures.Future()
    app.future.set_result((1, {"answer": "A", "total": 1}))
    app.tick()
    assert app.result is None


def test_invalid_provider_rejected():
    from beru.providers import answer

    with pytest.raises(ValueError, match="provider"):
        answer("Question", [], provider="unknown")


def test_null_citations_are_safe():
    from beru.providers import answer
    from unittest.mock import Mock

    response = Mock()
    response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": '{"answer":"A","citations":null,"uncertain":false}'}
                    ]
                }
            }
        ]
    }
    with (
        patch.dict("os.environ", {"GEMINI_API_KEY": "test"}),
        patch("beru.providers.load_env"),
        patch("beru.providers.requests.post", return_value=response),
    ):
        result = answer("Question", [])
        assert result["citations"] == []


def test_duplicate_citations_deduplicated():
    from beru.providers import answer
    from unittest.mock import Mock

    response = Mock()
    response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": '{"answer":"A","citations":[1,1],"uncertain":false}'}
                    ]
                }
            }
        ]
    }
    with (
        patch.dict("os.environ", {"GEMINI_API_KEY": "test"}),
        patch("beru.providers.load_env"),
        patch("beru.providers.requests.post", return_value=response),
    ):
        result = answer("Question", [{"text": "evidence"}])
        assert result["citations"] == [1]


def test_current_question_can_bypass_one_slow_obsolete_request(qtbot):
    app = make_app(qtbot)
    old = concurrent.futures.Future()
    app.future = old
    app.invalidate()
    assert app.future is None and old in app.obsolete
    current = concurrent.futures.Future()
    current.set_result(
        (app.generation, {"answer": "b. New", "uncertain": False, "total": 1})
    )
    app.future = current
    app.tick()
    assert app.result["answer"] == "b. New"
    old.set_result((app.generation - 1, {"answer": "a. Old", "total": 99}))
    app.tick()
    assert app.result["answer"] == "b. New"


def test_model_change_invalidates_pending(qtbot):
    app = make_app(qtbot)
    before = app.generation
    app.model.setCurrentText("gemini-4-argon")
    assert app.generation > before
