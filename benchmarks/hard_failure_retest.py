import json, pathlib, time
from benchmarks.hard_cases import cases
from benchmarks.hard_audit import task
from beru import semantic

OUT = pathlib.Path("research/hard-audit")
lookup = {c["id"]: c for c in cases()}
jobs = []
for mode in ["core", "permutations"]:
    for line in (OUT / f"{mode}.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["correct"]:
            continue
        c = lookup[r["id"]]
        if mode == "permutations":
            c = dict(
                c,
                options=list(reversed(c["options"])),
                gold=len(c["options"]) - 1 - c["gold"],
            )
        jobs.append((c, r["variant"], 4))
semantic.start()
deadline = time.monotonic() + 20
while not semantic._instance.ready and time.monotonic() < deadline:
    time.sleep(0.05)
with (OUT / "failure-retests.jsonl").open("w") as f:
    for job in jobs:
        r = task(job)
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        print(r["id"], r["correct"], r.get("error"), flush=True)
semantic.stop()
