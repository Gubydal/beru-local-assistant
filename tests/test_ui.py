import os, unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from beru.app import App


class UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_answer_and_evidence(self):
        window = App()
        self.assertFalse(window.details.isChecked())
        window.result = {
            "answer": "A",
            "uncertain": False,
            "explanation": "Explanation",
            "citations": [1],
            "evidence": [
                {"source": "course.md", "section": "Page 3", "text": "Evidence"}
            ],
        }
        window.render()
        self.assertEqual(window.output.toPlainText(), "A")
        window.details.setChecked(True)
        window.render()
        self.assertIn("Page 3", window.output.toPlainText())
        window.close()
