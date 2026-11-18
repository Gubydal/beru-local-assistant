"""Frozen hard-question benchmark. Modes are separately reported; cache is disabled."""

import json, time, pathlib, concurrent.futures, re, unicodedata, sys
from benchmarks.hard_cases import cases
from benchmarks.render import render
from benchmarks.run import label
from beru.engine import Engine
from beru import semantic

OUT = pathlib.Path("research/hard-audit")
OUT.mkdir(exist_ok=True)


def norm(s):
    s = s.replace("’", "'").replace("‘", "'")
    return " ".join(
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode()
        .lower()
        .replace("'", " ")
        .split()
    )


def task(job):
    c, variant, round = job
    t = time.monotonic()
    r = dict(
        id=c["id"],
        variant=variant,
        round=round,
        expected=c["gold"],
        expected_source=c["source"],
    )
    try:
        result = Engine().solve(
            render(c, variant), model="gemini-3.8-flash", use_cache=False
        )
        r["result"] = result
        r["correct"] = label(result["answer"]) == c["gold"]
        r["source_retrieved"] = any(
            c["source"] in e["source"] for e in result["evidence"]
        )
        cited = [result["evidence"][i - 1] for i in result.get("citations", [])]
        r["expected_source_cited"] = any(c["source"] in e["source"] for e in cited)
        r["evidence_anchor_present"] = any(
            norm(c["anchor"]) in norm(re.sub(r"\[\d+(?:\.\d+)?s\]", "", e["text"]))
            for e in result["evidence"]
        )
    except Exception as e:
        r.update(
            error=type(e).__name__,
            message=str(e)[:200],
            correct=False,
            abstained=type(e).__name__ == "Abstention",
        )
    r["total_seconds"] = time.monotonic() - t
    return r


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "core"
    semantic.start()
    deadline = time.monotonic() + 20
    while not semantic._instance.ready and time.monotonic() < deadline:
        time.sleep(0.05)
    if not semantic._instance.ready:
        raise SystemExit(
            "Semantic retrieval did not become ready; do not label this a hybrid benchmark."
        )
    jobs = (
        [(c, "question_only", 1) for c in cases()]
        if mode == "core"
        else [
            (c, v, 1)
            for c in cases()[::4]
            for v in ["clean", "selected_wrong", "blur", "jpeg"]
        ]
        if mode == "images"
        else [
            (
                dict(
                    c,
                    options=list(reversed(c["options"])),
                    gold=len(c["options"]) - 1 - c["gold"],
                ),
                "question_only",
                2,
            )
            for c in cases()
        ]
    )
    with (
        (OUT / f"{mode}.jsonl").open("w") as f,
        concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool,
    ):
        for i, r in enumerate(pool.map(task, jobs)):
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            if (i + 1) % 5 == 0:
                print(mode, i + 1, "/", len(jobs), flush=True)
    semantic.stop()
