import json, pathlib, concurrent.futures
from benchmarks.production import task
from benchmarks.cases import dataset
from beru import semantic
import time

root = pathlib.Path("research/benchmark")
lookup = {c["id"]: c for c in dataset()}
rows = []
for file in [
    "hardened-models.jsonl",
    "hardened-images.jsonl",
    "hardened-heldout.jsonl",
]:
    if (root / file).exists():
        for line in (root / file).read_text().splitlines():
            r = json.loads(line)
            if r.get("rejected") or r.get("correct") is False:
                rows.append(r)
jobs = list(
    {
        (r["id"], r["variant"], r["model"]): (lookup[r["id"]], r["variant"], r["model"])
        for r in rows
    }.values()
)
semantic.start()
until = time.monotonic() + 20
while not semantic._instance.ready and time.monotonic() < until:
    time.sleep(0.05)
with (
    (root / "retested-failures.jsonl").open("w") as f,
    concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool,
):
    for i, result in enumerate(pool.map(task, jobs)):
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
        f.flush()
        if (i + 1) % 10 == 0:
            print("Retested", i + 1, "/", len(jobs), flush=True)
if semantic._instance.process:
    semantic._instance.process.terminate()
