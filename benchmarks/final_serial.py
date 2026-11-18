import json, time, pathlib
from beru import semantic
from benchmarks.production import task
from benchmarks.cases import dataset
from benchmarks.heldout_cases import cases

semantic.start()
until = time.monotonic() + 20
while not semantic._instance.ready and time.monotonic() < until:
    time.sleep(0.05)
allcases = dataset() + cases()
root = pathlib.Path("research/benchmark")
with (root / "final-serial.jsonl").open("w") as f:
    for i, c in enumerate(allcases):
        r = task((c, "question_only", "gemini-3.8-flash"))
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        if (i + 1) % 5 == 0:
            print("Serial", i + 1, "/", len(allcases), flush=True)
if semantic._instance.process:
    semantic._instance.process.terminate()
