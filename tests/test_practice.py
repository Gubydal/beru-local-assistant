import json, threading, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
from beru.practice import Handler, ROOT


def test_practice_questions_have_valid_gold_and_unique_ids():
    questions = json.loads((ROOT / "questions.json").read_text())
    assert len(questions) == 29
    assert len({q["id"] for q in questions}) == 29
    assert all(0 <= q["gold"] < len(q["options"]) for q in questions)


def test_local_practice_server_serves_only_practice_assets():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urllib.request.urlopen(base + "/healthz") as response:
            assert json.load(response) == {"app": "beru-practice"}
        with urllib.request.urlopen(base + "/") as response:
            assert "Management interculturel" in response.read().decode()
        try:
            urllib.request.urlopen(base + "/API.env")
        except urllib.error.HTTPError as error:
            assert error.code == 404
        else:
            raise AssertionError("Workspace secret file must not be exposed")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_overlay_is_configured_as_persistent_tool_panel(qtbot):
    from PySide6.QtCore import Qt
    from beru.app import App

    window = App()
    window.timer.stop()
    qtbot.addWidget(window)
    assert window.windowType() == Qt.Tool
    assert window.testAttribute(Qt.WA_MacAlwaysShowToolWindow)
    assert window.testAttribute(Qt.WA_QuitOnClose)
    assert window.status.wordWrap()


def test_added_practice_sets_cover_priority_resources_with_source_anchors():
    from tests.test_hard_knowledge import normalize
    root=ROOT.parent
    for filename,count in [('questions-fundamentals.json',24),('questions-deep.json',28)]:
        rows=json.loads((ROOT/filename).read_text())
        assert len(rows)==count
        assert len({r['id'] for r in rows})==count
        assert {'DOC Support 5-1','DOC Support 6-1','DOC Support 6-2','9QdyxU7tseo','DOC Support 3-2'} <= {r['source'] for r in rows}
        for row in rows:
            assert 0 <= row['gold'] < len(row['options'])
            assert len(set(row['options']))==len(row['options'])
            sources=[p for p in (root/'knowledge').rglob('*.md') if p.stem==row['source']]
            assert sources and any(normalize(row['needle']) in normalize(p.read_text()) for p in sources),row['id']
            assert row['explanation']
