import json, time, pathlib
from benchmarks.cases import dataset
from benchmarks.production import task
from beru import semantic

semantic.start()
until = time.monotonic() + 20
while not semantic._instance.ready and time.monotonic() < until:
    time.sleep(0.05)
c = next(c for c in dataset() if c["id"] == "all_both_reordered")
with pathlib.Path("research/benchmark/corrected-permutation.jsonl").open("w") as f:
    for _ in range(3):
        r = task((c, "question_only", "gemini-3.8-flash"))
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        print(r.get("correct"), round(r["total_seconds"], 2), flush=True)
semantic.stop()
