"""Visible macOS check: open the local quiz, then inspect the inactive panel."""

import sys, json, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from beru.app import App
from beru.macos import configure_panel

app = QApplication([])
window = App()
window.show()
app.applicationStateChanged.connect(lambda _: QTimer.singleShot(50, window.pin_panel))
result = {}


def verify():
    state = configure_panel(window, apply=False)
    state["qt_active"] = window.isActiveWindow()
    state["application_state"] = app.applicationState().name
    result.update(state)
    Path("research/overlay-native-check.json").write_text(json.dumps(state, indent=2))
    print("After opening browser:", state, flush=True)
    window.close()
    app.quit()


QTimer.singleShot(
    500, lambda: subprocess.Popen(["/usr/bin/open", "http://127.0.0.1:8765/"])
)
QTimer.singleShot(4000, verify)
app.exec()
assert (
    result.get("level") == 25
    and result.get("visible") is True
    and result.get("hides_on_deactivate") is False
    and result.get("application_state") == "ApplicationInactive"
)
