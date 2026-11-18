"""Benchmark the exact Engine used by the desktop app, with API cache disabled."""

import json, time, pathlib, concurrent.futures, statistics, sys
from benchmarks.cases import dataset
from benchmarks.render import render, VARIANTS
from benchmarks.run import label
from beru.engine import Engine
from beru import semantic

OUT = pathlib.Path("research/benchmark")


def task(job):
    case, variant, model = job
    engine = Engine()
    started = time.monotonic()
    r = dict(id=case["id"], variant=variant, model=model, expected=case["gold"])
    try:
        result = engine.solve(render(case, variant), model=model, use_cache=False)
        r["result"] = result
        r["correct"] = (
            result["uncertain"]
            if case["gold"] is None
            else label(result["answer"]) == case["gold"]
        )
    except Exception as exc:
        r.update(error=type(exc).__name__, message=str(exc)[:180], rejected=True)
    r["total_seconds"] = time.monotonic() - started
    r["expected_rejection"] = variant in ["partial", "blank"]
    return r


if __name__ == "__main__":
    matrix = sys.argv[1] if len(sys.argv) > 1 else "models"
    tag = sys.argv[2] if len(sys.argv) > 2 else "hardened"
    semantic.start()
    until = time.monotonic() + 20
    while not semantic._instance.ready and time.monotonic() < until:
        time.sleep(0.05)
    if matrix == "models":
        jobs = [
            (c, "question_only", m)
            for c in dataset()
            for m in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-4-argon"]
        ]
    elif matrix == "images":
        jobs = [(c, v, "gemini-3.8-flash") for c in dataset()[::2] for v in VARIANTS]
    elif matrix == "heldout":
        jobs = [
            (c, v, "gemini-3.8-flash")
            for c in dataset()[::2]
            for v in [
                "severe_blur",
                "perspective",
                "moire",
                "glare",
                "micro",
                "cropped_choice",
                "retina",
            ]
        ]
    results = []
    with (
        (OUT / f"{tag}-{matrix}.jsonl").open("w") as f,
        concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool,
    ):
        for r in pool.map(task, jobs):
            results.append(r)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            if len(results) % 10 == 0:
                print("Completed", len(results), "/", len(jobs), flush=True)
    summary = {}
    for model in sorted(set(r["model"] for r in results)):
        rows = [r for r in results if r["model"] == model]
        valid = [r for r in rows if "correct" in r and not r["expected_rejection"]]
        times = sorted(r["total_seconds"] for r in valid)
        summary[model] = dict(
            n=len(rows),
            answered=len(valid),
            correct=sum(r["correct"] for r in valid),
            unexpected_rejections=sum(
                r.get("rejected", False) and not r["expected_rejection"] for r in rows
            ),
            expected_rejections=sum(
                r.get("rejected", False) and r["expected_rejection"] for r in rows
            ),
            p50=statistics.median(times) if times else None,
            p95=times[min(len(times) - 1, int(0.95 * len(times)))] if times else None,
            over_15=sum(t > 15 for t in times),
        )
    (OUT / f"{tag}-{matrix}-summary.json").write_text(json.dumps(summary, indent=2))
    print(summary, flush=True)
    if semantic._instance.process:
        semantic._instance.process.terminate()
