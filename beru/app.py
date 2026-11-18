import sys, time, concurrent.futures
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QComboBox,
    QSizeGrip,
    QCheckBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCursor
from beru.engine import Engine
from beru.watcher import fingerprint, changed
from beru.knowledge import index


class Selector(QWidget):
    """A movable, resizable capture frame; only its transparent center is captured."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.drag_origin = None
        self.setWindowTitle("Select capture area")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setMinimumSize(320, 180)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        toolbar = QWidget()
        toolbar.setStyleSheet("background:#193d60;color:white;border-radius:5px;")
        controls = QHBoxLayout(toolbar)
        controls.setContentsMargins(10, 7, 10, 7)
        label = QLabel("Move / resize")
        label.setAttribute(Qt.WA_TransparentForMouseEvents)
        controls.addWidget(label)
        controls.addStretch()
        self.confirm_button = QPushButton("Use area")
        self.confirm_button.clicked.connect(self.confirm)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.close)
        controls.addWidget(self.confirm_button)
        controls.addWidget(cancel)
        layout.addWidget(toolbar)
        self.canvas = QWidget()
        self.canvas.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.canvas.setStyleSheet(
            "background:rgba(60,130,200,25);border:2px dashed #3c82c8;"
        )
        layout.addWidget(self.canvas, 1)
        bottom = QWidget()
        bottom.setStyleSheet("background:#193d60;color:white;")
        footer = QHBoxLayout(bottom)
        footer.setContentsMargins(10, 0, 2, 0)
        tip = QLabel("Enter: use area · Esc: cancel")
        tip.setAttribute(Qt.WA_TransparentForMouseEvents)
        footer.addWidget(tip)
        footer.addStretch()
        footer.addWidget(QSizeGrip(self))
        layout.addWidget(bottom)
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        available = screen.availableGeometry()
        self.resize(
            min(760, int(available.width() * 0.65)),
            min(440, int(available.height() * 0.55)),
        )
        self.move(available.center() - self.rect().center())
        self.show()
        from beru.macos import configure_panel

        QTimer.singleShot(
            0, lambda: configure_panel(self) if self.isVisible() else None
        )

    def confirm(self):
        rect = self.canvas.rect()
        pos = self.canvas.mapToGlobal(rect.topLeft())
        if rect.width() < 20 or rect.height() < 20:
            return
        region = {
            "left": pos.x(),
            "top": pos.y(),
            "width": rect.width(),
            "height": rect.height(),
        }
        self.close()
        self.callback(region)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.confirm()
        else:
            super().keyPressEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_origin = (
                e.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            e.accept()

    def mouseMoveEvent(self, e):
        if self.drag_origin is not None and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self.drag_origin)
            e.accept()

    def mouseReleaseEvent(self, e):
        self.drag_origin = None


class App(QWidget):
    def __init__(self):
        super().__init__()
        from beru.semantic import start

        start()
        self.setWindowTitle("Beru")
        self.setWindowFlags(
            Qt.Tool
            | Qt.WindowStaysOnTopHint
            | Qt.WindowTitleHint
            | Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setAttribute(Qt.WA_QuitOnClose, True)
        self.resize(420, 320)
        self.question_box = None
        self.engine = Engine()
        self.obsolete = []
        self.region = None
        self.previous = None
        self.stable = 0
        self.generation = 0
        self.pending = None
        self.future = None
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.running = False
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        layout.addLayout(row)
        for text, callback in [
            ("Select area", self.select),
            ("Watch / pause", self.toggle),
            ("Capture", self.capture),
            ("Index sources", self.reindex),
        ]:
            b = QPushButton(text)
            b.clicked.connect(callback)
            row.addWidget(b)
        self.provider = QComboBox()
        self.provider.addItems(["gemini", "deepseek"])
        layout.addWidget(self.provider)
        self.model = QComboBox()
        self.model.addItems(
            ["gemini-3.8-flash", "gemini-4-hydrogen", "gemini-4-argon", "gemini-3.5-flash-lite"]
        )
        layout.addWidget(self.model)
        self.provider.currentTextChanged.connect(self.change_provider)
        self.model.currentTextChanged.connect(lambda _: self.invalidate())
        self.visual = QCheckBox("Include image for diagrams")
        layout.addWidget(self.visual)
        self.status = QLabel("Select a question area. Keep this panel outside it.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        self.details = QPushButton("Show evidence")
        self.details.setCheckable(True)
        self.details.clicked.connect(self.render)
        layout.addWidget(self.details)
        self.result = None
        self.cache = self.engine.cache

        if sys.platform == "darwin":
            import ctypes

            cg = ctypes.CDLL(
                "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
            )
            cg.CGPreflightScreenCaptureAccess.restype = ctypes.c_bool
            if not cg.CGPreflightScreenCaptureAccess():
                self.status.setText(
                    "Enable Screen Recording for your terminal/app in macOS Privacy settings."
                )
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(300)

    def change_provider(self, provider):
        self.invalidate()
        self.model.blockSignals(True)
        self.model.clear()
        self.model.addItems(
            ["gemini-3.8-flash", "gemini-4-hydrogen", "gemini-4-argon", "gemini-3.5-flash-lite"]
            if provider == "gemini"
            else ["deepseek-flash"]
        )
        self.model.blockSignals(False)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.pin_panel)

    def pin_panel(self):
        from beru.macos import configure_panel

        if self.isVisible():
            return configure_panel(self)
        return False

    def select(self):
        self.running = False
        self.invalidate()
        self.pending = None
        self.selector = Selector(self.set_region)

    def set_region(self, r):
        self.region = r
        self.previous = None
        self.question_box = None
        self.invalidate()
        self.status.setText("Area selected. Press Watch or Capture.")

    def toggle(self):
        self.running = not self.running
        if not self.running:
            self.invalidate()
            self.pending = None
        else:
            self.previous = None
            self.stable = 0
        self.status.setText("Watching" if self.running else "Paused")

    def reindex(self):
        if self.future is not None or any(not f.done() for f in self.obsolete):
            self.status.setText(
                "Pause and wait for the current answer before indexing."
            )
            return
        self.running = False
        self.invalidate()
        self.pending = None
        self.cache.clear()
        self.status.setText(
            f"Indexed {index()} passages; rebuild vectors for semantic search"
        )

    def capture_image(self):
        import mss
        from PIL import Image

        with mss.mss() as s:
            shot = s.grab(self.region)
            return Image.frombytes("RGB", shot.size, shot.rgb)

    def capture(self):
        self.running = False
        if not self.region:
            self.status.setText("Select a question area first.")
            return
        try:
            self.invalidate()
            self.pending = (
                self.generation,
                self.capture_image(),
                self.provider.currentText(),
                time.monotonic(),
                self.visual.isChecked(),
                True,
                self.model.currentText(),
            )
            self.dispatch()
        except Exception as exc:
            self.status.setText("Capture failed: " + str(exc)[:150])

    def dispatch(self):
        if self.pending and self.future is None:
            item = self.pending
            self.pending = None
            self.future = self.pool.submit(self.solve, *item)
            self.status.setText("Reading and searching…")

    def solve(
        self,
        generation,
        image,
        provider,
        started,
        visual=False,
        force=False,
        model=None,
    ):
        def on_read(question):
            if generation == self.generation:
                self.question_box = question.box
                self.previous = fingerprint(image, question.box)
                self.stable = 3

        result = self.engine.solve(
            image, provider, visual, model=model, on_read=on_read, refresh=force
        )
        result["total"] = time.monotonic() - started
        return generation, result

    def invalidate(self):
        self.generation += 1
        self.pending = None
        self.obsolete = [f for f in self.obsolete if not f.done()]
        if self.future and not self.future.done() and not self.obsolete:
            self.obsolete.append(self.future)
            self.future = None

    def tick(self):
        try:
            if self.running and self.region:
                image = self.capture_image()
                small = fingerprint(image, self.question_box)
                has_changed = changed(self.previous, small)
                self.previous = small
                if has_changed:
                    self.invalidate()
                    self.stable = 0
                    self.pending = None
                    self.result = None
                    self.output.setPlainText("New question…")
                else:
                    self.stable += 1
                    if self.stable == 2:
                        self.pending = (
                            self.generation,
                            image,
                            self.provider.currentText(),
                            time.monotonic(),
                            self.visual.isChecked(),
                            False,
                            self.model.currentText(),
                        )
            if self.future and self.future.done():
                future = self.future
                self.future = None
                try:
                    generation, result = future.result()
                    if generation == self.generation:
                        self.result = result
                        self.render()
                        self.status.setText(
                            f"{result['total']:.1f}s total"
                            + (" · cached" if result.get("cached") else "")
                        )
                except Exception as e:
                    self.status.setText(str(e)[:200])
            self.dispatch()
        except Exception as e:
            self.running = False
            self.status.setText("Capture failed: " + str(e)[:150])

    def closeEvent(self, event):
        self.timer.stop()
        self.running = False
        self.invalidate()
        self.pending = None
        self.pool.shutdown(wait=False, cancel_futures=True)
        event.accept()

    def render(self):
        if not self.result:
            return
        r = self.result
        text = str(r.get("answer", "No answer")) + (
            " ⚠ uncertain" if r.get("uncertain", True) else ""
        )
        if self.details.isChecked():
            text += "\n\n" + r.get("explanation", "") + "\n\n"
            for i in r.get("citations", []):
                e = r["evidence"][i - 1]
                text += f"[{i}] {e['source']} — {e['section']}\n{e['text']}\n\n"
        self.output.setPlainText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    app.applicationStateChanged.connect(
        lambda _: QTimer.singleShot(50, window.pin_panel)
    )
    sys.exit(app.exec())
