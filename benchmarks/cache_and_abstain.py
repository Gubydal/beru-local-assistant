import json, time, pathlib
from beru import semantic
from beru.engine import Engine
from benchmarks.cases import dataset
from benchmarks.render import render

semantic.start()
deadline = time.monotonic() + 20
while not semantic._instance.ready and time.monotonic() < deadline:
    time.sleep(0.05)
e = Engine()
image = render(dataset()[0], "question_only")
times = []
for i in range(4):
    r = e.solve(image)
    times.append({"total": r["total"], "cached": r["cached"], "answer": r["answer"]})
case = next(c for c in dataset() if c["id"] == "unsupported")
try:
    r = e.solve(render(case, "question_only"), use_cache=False)
    unknown = {"uncertain": r["uncertain"], "answer": r["answer"]}
except Exception as exc:
    unknown = {"exception": type(exc).__name__, "message": str(exc)}
pathlib.Path("research/benchmark/cache-and-abstain.json").write_text(
    json.dumps({"cache": times, "unknown": unknown}, ensure_ascii=False, indent=2)
)
print(times, unknown)
semantic.stop()
