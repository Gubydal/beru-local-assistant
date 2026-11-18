"""Fresh serial verification after capture-parser repairs; earlier results preserved."""

import json, pathlib, time
from benchmarks.hard_cases import cases
from benchmarks.hard_audit import task
from beru import semantic

OUT = pathlib.Path("research/hard-audit")
semantic.start()
deadline = time.monotonic() + 20
while not semantic._instance.ready and time.monotonic() < deadline:
    time.sleep(0.05)
with (OUT / "final-serial.jsonl").open("w") as f:
    for i, c in enumerate(cases()):
        r = task((c, "question_only", 3))
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        if (i + 1) % 5 == 0:
            print("Final hard serial", i + 1, "/40", flush=True)
semantic.stop()
