import json, time, pathlib
from beru.engine import Engine
from beru import semantic
from benchmarks.render import render
from benchmarks.cases import dataset
from benchmarks.run import label

semantic.start()
until = time.monotonic() + 20
while not semantic._instance.ready and time.monotonic() < until:
    time.sleep(0.05)
with pathlib.Path("research/benchmark/visual-recovery.jsonl").open("w") as f:
    for c in [c for c in dataset() if c["id"] in ["social", "power", "individualism"]]:
        for variant in ["micro", "moire", "severe_blur", "cropped_choice"]:
            t = time.monotonic()
            r = {"id": c["id"], "variant": variant, "expected": c["gold"]}
            try:
                result = Engine().solve(
                    render(c, variant),
                    visual=True,
                    model="gemini-3.8-flash",
                    use_cache=False,
                )
                r.update(result=result, correct=label(result["answer"]) == c["gold"])
            except Exception as e:
                r.update(error=type(e).__name__, message=str(e)[:200])
            r["total_seconds"] = time.monotonic() - t
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            print(
                c["id"],
                variant,
                r.get("correct", r.get("error")),
                round(r["total_seconds"], 2),
                flush=True,
            )
if semantic._instance.process:
    semantic._instance.process.terminate()
