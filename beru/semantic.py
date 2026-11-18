import subprocess, threading, json, queue, pathlib, time, atexit

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Semantic:
    def __init__(self):
        self.root = ROOT
        self.stamp = (
            (ROOT / "knowledge/semantic.npz").stat().st_mtime_ns
            if (ROOT / "knowledge/semantic.npz").exists()
            else None
        )
        self.created_at = time.monotonic()
        self.ready = False
        self.process = None
        self.responses = queue.Queue()
        self.lock = threading.Lock()
        threading.Thread(target=self.start, daemon=True).start()

    def start(self):
        if not all(
            p.exists()
            for p in [
                self.root / "knowledge/semantic.npz",
                self.root / ".media-venv/bin/python",
                self.root / "scripts/semantic_worker.py",
            ]
        ):
            return
        try:
            self.process = subprocess.Popen(
                [
                    str(self.root / ".media-venv/bin/python"),
                    str(self.root / "scripts/semantic_worker.py"),
                    "search",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
        except OSError:
            self.ready = False
            return
        for line in self.process.stdout:
            try:
                data = json.loads(line)
                if data.get("ready"):
                    self.ready = True
                else:
                    self.responses.put(data)
            except ValueError:
                pass
        self.ready = False

    def search(self, question):
        if not self.ready:
            return []
        with self.lock:
            try:
                self.process.stdin.write(json.dumps({"query": question}) + "\n")
                self.process.stdin.flush()
                return self.responses.get(timeout=2)["hits"]
            except Exception:
                if self.process:
                    self.process.terminate()
                self.ready = False
                return []


_instance = None
_start_lock = threading.Lock()


def _start():
    global _instance
    stamp = (
        (ROOT / "knowledge/semantic.npz").stat().st_mtime_ns
        if (ROOT / "knowledge/semantic.npz").exists()
        else None
    )
    if (
        _instance is None
        or _instance.stamp != stamp
        or (
            not _instance.ready
            and time.monotonic() - _instance.created_at > 30
            and (_instance.process is None or _instance.process.poll() is not None)
        )
    ):
        if _instance and _instance.process:
            _instance.process.terminate()
        _instance = Semantic()


def start():
    with _start_lock:
        _start()


def search(question):
    start()
    return _instance.search(question)


def stop():
    global _instance
    with _start_lock:
        if _instance and _instance.process:
            try:
                _instance.process.terminate()
                _instance.process.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired):
                pass
        _instance = None


atexit.register(stop)
