import sys, json, time, pathlib, subprocess, re, concurrent.futures, statistics

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from benchmarks.cases import dataset
from benchmarks.render import render, VARIANTS
from beru.knowledge import search
from beru.providers import answer
from beru import semantic

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "research/benchmark"
OUT.mkdir(exist_ok=True)


def label(value):
    match = re.match(r"^[^\w]*([a-f])(?:[.\s):]|$)", str(value), re.I)
    return ord(match[1].lower()) - 97 if match else None


def run_one(case, variant, model, live):
    started = time.monotonic()
    image = render(case, variant)
    path = OUT / "fixtures" / f"{case['id']}--{variant}.png"
    path.parent.mkdir(exist_ok=True)
    image.save(path)
    r = {"id": case["id"], "variant": variant, "model": model, "expected": case["gold"]}
    try:
        t = time.monotonic()
        ocr = subprocess.check_output(
            [str(ROOT / "bin/beru-ocr"), str(path)], text=True, timeout=15
        ).strip()
        r["ocr_seconds"] = time.monotonic() - t
        r["ocr"] = ocr
        r["option_labels_read"] = len(
            re.findall(r"(?im)^\s*(?:[oO○●]\s*)?[a-f][.\s)]", ocr)
        )
        t = time.monotonic()
        evidence = search(ocr)
        r["retrieval_seconds"] = time.monotonic() - t
        r["retrieval_hit"] = any(
            case.get("source") and case["source"] in e["source"] for e in evidence
        )
        r["evidence"] = [
            {"source": e["source"], "section": e["section"]} for e in evidence
        ]
        if live:
            t = time.monotonic()
            result = answer(ocr, evidence, model=model)
            r["model_seconds"] = time.monotonic() - t
            r["result"] = result
            r["correct"] = (
                result.get("uncertain") is True
                if case["gold"] is None
                else label(result["answer"]) == case["gold"]
            )
        r["total_seconds"] = time.monotonic() - started
    except Exception as exc:
        r["error"] = type(exc).__name__
        r["total_seconds"] = time.monotonic() - started
    return r


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true")
    p.add_argument("--tag", default="baseline")
    p.add_argument("--matrix", choices=["ocr", "models", "images"], default="ocr")
    args = p.parse_args()
    semantic.start()
    deadline = time.monotonic() + 20
    while not semantic._instance.ready and time.monotonic() < deadline:
        time.sleep(0.05)
    cases = dataset()
    jobs = []
    if args.matrix == "ocr":
        jobs = [(c, v, "gemini-3.8-flash", False) for c in cases[::2] for v in VARIANTS]
    if args.matrix == "models":
        jobs = [
            (c, "question_only", m, True)
            for c in cases
            for m in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-4-argon"]
        ]
    if args.matrix == "images":
        jobs = [
            (c, v, "gemini-3.8-flash", True)
            for c in cases[::2]
            for v in ["clean", "tiny", "blur", "selected_wrong"]
        ]
    results = []
    target = OUT / f"{args.tag}-{args.matrix}.jsonl"
    with (
        target.open("w") as f,
        concurrent.futures.ThreadPoolExecutor(
            max_workers=3 if args.live else 2
        ) as pool,
    ):
        for r in pool.map(lambda job: run_one(*job), jobs):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            results.append(r)
            if len(results) % 10 == 0:
                print("Completed", len(results), "/", len(jobs), flush=True)
    summary = {
        "cases": len(results),
        "errors": sum("error" in r for r in results),
        "semantic_ready": semantic._instance.ready,
    }
    live = [r for r in results if "correct" in r]
    if live:
        summary["accuracy"] = sum(r["correct"] for r in live) / len(live)
        times = sorted(r["total_seconds"] for r in live)
        summary.update(
            p50=statistics.median(times),
            p95=times[min(len(times) - 1, int(0.95 * len(times)))],
            over_15=sum(t > 15 for t in times),
        )
    (OUT / f"{args.tag}-{args.matrix}-summary.json").write_text(
        json.dumps(summary, indent=2)
    )
    print(summary, flush=True)
    if semantic._instance.process:
        semantic._instance.process.terminate()


if __name__ == "__main__":
    main()
