import concurrent.futures, time
from unittest.mock import patch
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QPoint
from PIL import Image
from beru.app import App, Selector


def window(qtbot):
    w = App()
    w.timer.stop()
    qtbot.addWidget(w)
    return w


def test_centered_area_can_be_adjusted_and_confirmed(qtbot):
    seen = []
    s = Selector(seen.append)
    qtbot.addWidget(s)
    available = s.screen().availableGeometry()
    assert s.width() < available.width() and s.height() < available.height()
    s.move(s.x() + 30, s.y() + 20)
    s.resize(600, 350)
    qtbot.wait(20)
    expected = s.canvas.mapToGlobal(QPoint(0, 0))
    qtbot.mouseClick(s.confirm_button, Qt.LeftButton)
    assert (
        len(seen) == 1
        and seen[0]["left"] == expected.x()
        and seen[0]["top"] == expected.y()
    )
    assert (
        seen[0]["width"] == s.canvas.width() and seen[0]["height"] == s.canvas.height()
    )
    assert not s.isVisible()


def test_selection_cancel_does_not_capture(qtbot):
    seen = []
    s = Selector(seen.append)
    qtbot.addWidget(s)
    qtbot.keyClick(s, Qt.Key_Escape)
    assert not seen and not s.isVisible()


def test_manual_capture_without_area_is_actionable(qtbot):
    w = window(qtbot)
    w.capture()
    assert "Select" in w.status.text()


def test_provider_change_resets_model_and_pending_request(qtbot):
    w = window(qtbot)
    w.pending = ("old",)
    w.provider.setCurrentText("deepseek")
    assert w.model.currentText() == "deepseek-flash" and w.pending is None


def test_reindex_waits_for_obsolete_work(qtbot):
    w = window(qtbot)
    w.obsolete = [concurrent.futures.Future()]
    with patch("beru.app.index") as index:
        w.reindex()
        index.assert_not_called()
        assert "wait" in w.status.text()


def test_reindex_clears_cache_and_pauses(qtbot):
    w = window(qtbot)
    w.running = True
    w.cache["old"] = {}
    with patch("beru.app.index", return_value=10):
        w.reindex()
    assert not w.running and not w.cache and "10" in w.status.text()


def test_manual_capture_dispatches_refresh_with_model(qtbot):
    w = window(qtbot)
    w.region = {"left": 0, "top": 0, "width": 50, "height": 50}
    future = concurrent.futures.Future()
    with (
        patch.object(w, "capture_image", return_value=Image.new("RGB", (50, 50))),
        patch.object(w.pool, "submit", return_value=future) as submit,
    ):
        button = next(b for b in w.findChildren(QPushButton) if b.text() == "Capture")
        qtbot.mouseClick(button, Qt.LeftButton)
        assert submit.call_args.args[-4:] == (True, "gemini-3.8-flash", "mcq", "coi")
    future.set_result(
        (w.generation, {"answer": "a. Correct", "uncertain": False, "total": 1})
    )
    w.tick()
    assert w.output.toPlainText() == "a. Correct"


def test_continuous_capture_error_pauses_cleanly(qtbot):
    w = window(qtbot)
    w.running = True
    w.region = {"left": 0, "top": 0, "width": 50, "height": 50}
    with patch.object(
        w, "capture_image", side_effect=PermissionError("Screen disabled")
    ):
        w.tick()
    assert not w.running and "Screen" in w.status.text()


def test_ocr_question_mask_does_not_invalidate_its_own_request(qtbot):
    from beru.question import Question
    from benchmarks.render import render
    from benchmarks.cases import dataset

    w = window(qtbot)
    image = render(dataset()[0])
    generation = w.generation
    q = Question("Question", {"a": "One", "b": "Two"}, 1, (0.1, 0.37, 0.74, 0.79))

    def fake(*args, **kwargs):
        kwargs["on_read"](q)
        return {"answer": "a. One", "total": 1, "uncertain": False}

    with patch.object(w.engine, "solve", side_effect=fake):
        w.solve(generation, image, "gemini", time.monotonic())
    w.running = True
    w.region = {"left": 0, "top": 0, "width": 1280, "height": 720}
    with patch.object(w, "capture_image", return_value=image):
        w.tick()
    assert w.generation == generation and w.pending is None


def test_manual_capture_pauses_automatic_monitoring(qtbot):
    w = window(qtbot)
    w.running = True
    w.region = {"left": 0, "top": 0, "width": 50, "height": 50}
    future = concurrent.futures.Future()
    with (
        patch.object(w, "capture_image", return_value=Image.new("RGB", (50, 50))),
        patch.object(w.pool, "submit", return_value=future),
    ):
        w.capture()
    assert not w.running
    future.cancel()
