import json, pathlib, statistics, hashlib, platform, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "research/benchmark"


def load(name):
    p = OUT / name
    return [json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []


def percentile(values, p):
    values = sorted(values)
    return values[min(len(values) - 1, int(p * len(values)))] if values else 0


serial = load("final-serial.jsonl")
valid = [r for r in serial if r["expected"] is not None]
corrected = load("corrected-permutation.jsonl")
cohort = valid
legacy = load("serial-before-dataset-fix.jsonl")
coverage_text = (OUT / "coverage.txt").read_text()
test_count = int(re.search(r"(\d+) passed", coverage_text)[1])
coverage_percent = json.loads((OUT / "coverage.json").read_text())["totals"][
    "percent_covered"
]
times = [r["total_seconds"] for r in cohort]
baseline = load("baseline-models.jsonl")
images = load("hardened-images.jsonl")
photos = load("hardened-heldout.jsonl")
retry = load("retested-failures.jsonl")
vision = load("visual-recovery.jsonl")
adversarial = load("adversarial.jsonl")
from benchmarks.run import label

summary = {
    "automated_checks": test_count,
    "statement_coverage_percent": coverage_percent,
    "final_valid_serial_cases": len(valid),
    "final_valid_serial_correct": sum(r.get("correct", False) for r in valid),
    "corrected_permutation_repeats": len(corrected),
    "corrected_permutation_correct": sum(r.get("correct", False) for r in corrected),
    "corrected_cohort_cases": len(cohort),
    "corrected_cohort_correct": sum(r.get("correct", False) for r in cohort),
    "p50_seconds": statistics.median(times),
    "p95_seconds": percentile(times, 0.95),
    "max_seconds": max(times),
    "original_invalid_case_seconds": next(
        r["total_seconds"] for r in legacy if r["id"] == "all_both_reordered"
    ),
    "visual_recovery_answered": sum("result" in r for r in vision),
    "visual_recovery_correct": sum(r.get("correct", False) for r in vision),
    "visual_recovery_rejected": sum("error" in r for r in vision),
    "adversarial_cases": len(adversarial),
    "adversarial_correct": sum(r.get("correct", False) for r in adversarial),
}
(OUT / "summary.json").write_text(json.dumps(summary, indent=2))
lines = [
    "# Deep evaluation and repairs",
    "",
    "## Outcome",
    "",
    f"{test_count} automated checks pass, covering {coverage_percent:.1f}% of Python statements. Covered statements do not prove all branches or OS behavior. In a fresh final serial run after the corpus and dataset repairs, {summary['final_valid_serial_correct']}/{len(valid)} valid source-answerable cases were correct. An earlier defective shuffled case was corrected and separately passed {summary['corrected_permutation_correct']}/{len(corrected)} repeat runs. The fresh 46-case cohort has median {summary['p50_seconds']:.2f}s, p95 {summary['p95_seconds']:.2f}s and maximum {summary['max_seconds']:.2f}s. This is a small synthetic benchmark, not a real-assessment accuracy estimate.",
    "",
    "A separate unknown-answer question produced a typed abstention. Cached repeats took 0.15–0.17s. The original 20.44s response to a malformed generated choice is preserved in serial-before-dataset-fix.jsonl; its correction is recorded separately, not silently overwritten. No hard 15-second guarantee is established.",
    "",
    "## Tools and coverage",
    "",
    "Used [pytest-qt](https://github.com/pytest-dev/pytest-qt) with pytest for actual PySide6 event/state tests. A purpose-built harness calls the same Engine as the desktop app, with answer caching disabled for accuracy/latency runs. API tests use real Google requests; ordinary pytest runs mock network calls and do not spend API credits.",
    "",
    "- 16 initial course-based questions, reversed choices, 16 additional source-anchored questions, unsupported questions, negations, near-identical MOINS/PLUS options, both/all answers and prompt injection.",
    "- 208 initial OCR cases across clean/full-page/cropped-card, wrong selected radio button, tiny text, blur, heavy blur, low contrast, darkness, rotation, JPEG, partial/blank capture and pixel noise.",
    "- 112 photo-style stress runs: micro text, severe blur, perspective, moiré, glare, missing choices and 2× Retina-sized images.",
    "- 93 baseline model requests; 93 intermediate production model runs; 208 production image-condition runs; 105 failure-only retests; two serial rounds of 47 cases; 12 explicit visual-recovery runs; five adversarial source/instruction tests; corrected permutation repeats and cache tests.",
    "- A temporary 50,001-passage keyword index was queried 20 times without changing the real corpus. Median 0.00043s, maximum 0.00230s. This measures keyword lookup only, not embedding ingestion or full-scale vector retrieval.",
    "",
    "The original attached photographs were used as visual references to reconstruct similar Moodle fixtures. Their original image bytes were not available to the local harness. Therefore these results do not certify OCR accuracy on those exact photos. Duplicate attached views are not independent test cases.",
    "",
    "## Baseline model comparison (validated source-answerable cases)",
    "",
    "| Model | Correct / valid cases | Median latency | p95 latency |",
    "|---|---:|---:|---:|",
]
for model in ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-4-argon"]:
    rows = [
        r
        for r in baseline
        if r["model"] == model
        and r["expected"] is not None
        and r["id"] != "all_both_reordered"
    ]
    ts = [r["total_seconds"] for r in rows]
    correct = sum(label(r["result"]["answer"]) == r["expected"] for r in rows)
    lines.append(
        f"| {model} | {correct}/{len(rows)} | {statistics.median(ts):.2f}s | {percentile(ts, 0.95):.2f}s |"
    )
lines += [
    "",
    "Flash-Lite confused subtle concepts even when its explanation mentioned the correct definition. Its incorrect answers included individualism as self-only and the reversed power-distance options. It remains optional. Gemini 3.8 Flash remains the default. Argon is optional and exceeded 15 seconds in two intermediate runs. DeepSeek remains unbenchmarked because no DeepSeek key was supplied.",
    "",
    "## Stress failures and conservative behavior",
    "",
    "| Intermediate stress suite | Runs | Answered | Passed answer/uncertainty checks | Rejected |",
    "|---|---:|---:|---:|---:|",
]
for name, rows in [
    ("Ordinary image variations", images),
    ("Photo-style variations", photos),
]:
    lines.append(
        f"| {name} | {len(rows)} | {sum('result' in r for r in rows)} | {sum(r.get('correct', False) for r in rows)} | {sum(r.get('rejected', False) for r in rows)} |"
    )
lines += [
    "",
    "These intermediate matrices intentionally preserve failures from earlier versions. Photo stress contained one wrong answer after an entire correct option was cropped away. The prompt was tightened to abstain when no visible option is supported, and that failure was rejected on retest. A local preprocessing retry and dropped-punctuation parser fix recovered additional captures. Failure-only retesting is regression evidence, not an unbiased new accuracy estimate.",
    "",
    f"With explicit image permission enabled, visual recovery answered {summary['visual_recovery_answered']}/12 tested hard captures; {summary['visual_recovery_correct']} answers were correct and {summary['visual_recovery_rejected']} captures were rejected. It sometimes requires two cloud calls and reached 14.82s in this small sample. Severe blur and missing whole choices remain real limits.",
    "",
    "## Repairs implemented",
    "",
    "- Replaced the coarse whole-image difference check that missed small text changes with a finer fingerprint. The OCR-derived question bounds exclude the Moodle timer and navigation from monitoring.",
    "- Canonicalized question text, preserving negation and choice order, so timer/radio changes do not invalidate answer identity.",
    "- Validated complete visible option labels; rejected empty, unreadable, missing-label and multiple-question captures. Accepted radio-marked labels when OCR drops the period.",
    "- Added one bounded local preprocessing retry; optional visual recovery requires the existing image checkbox. No background image upload when unchecked.",
    "- Shared a single Engine between desktop app and benchmark, with per-stage timing and explicit cached/model/visual-recovery metadata. Short source passages are retained instead of being silently discarded.",
    "- Fixed Pause/close queue invalidation, stale/out-of-order answers, manual capture permission errors, and Escape cancellation. Manual Capture pauses automatic monitoring so animated page changes cannot repeatedly invalidate a manual request.",
    "- Allowed one current request to bypass one obsolete slow request while bounding solver concurrency to two. Finite HTTP timeouts remain; this is not unlimited cancellation.",
    "- Scoped cache identity to model, provider, question, image and corpus version. Manual Capture refreshes and replaces cached results; an older overlapping request cannot overwrite a newer cache entry.",
    "- Separated trusted provider instructions from untrusted question/evidence text. Added model-option validation and typed abstention.",
    "- Hardened empty/blocked/malformed provider responses, null/duplicate/out-of-range citations, missing explanations, and missing keys. Unsupported citations cannot create a confident grounded result.",
    "- Bound vector IDs to a digest of their evidence rows. Missing/crashed/stale vector workers fall back to keyword search and retry with a delay instead of crashing or silently mismatching evidence.",
    "- Fixed generated-test defects: leading bullet grading, self-referential shuffled both-options, and a shared random generator in image-noise fixtures. Raw earlier outcomes remain available.",
    "",
    "## Remaining limits",
    "",
    "- Entire options can be omitted by a crop without any clipped characters. Screenshots alone cannot reliably prove the full choice list is visible; select the entire question card. The optional browser-reader idea was not implemented, per preference to keep the app separate from Moodle.",
    "- Real logged-in Moodle sessions, physical Retina/mixed-display setups, scrolling and fullscreen interactions still require user validation. Automated offscreen/native-helper checks cannot replace those tests.",
    "- Machine transcripts/OCR, survey charts and generated source notes are not human-verified. Bounds-checked citations are not a proof of semantic support. Adversarial checks passed in five examples but do not establish universal prompt-injection resistance.",
    "- Network tails, rate limits and hard questions can exceed 15 seconds. Severe degradation may require recapture or image recovery. Rejection/abstention is safer than inventing unreadable choices.",
    "- Multi-select checkboxes, multi-question pages, unseen website layouts and inaccessible/occluded text are not established capabilities.",
    "- No browser injection, automated clicks or login access was added. No guarantee of undetectability is made.",
    "- Cases include near-duplicates and option permutations, and were derived from the same course corpus used for retrieval. Do not interpret 46/46 as a generalization guarantee or a statistical estimate for future exams.",
    "",
    "## Reproduce",
    "",
    "```sh",
    "uv pip install --python .venv/bin/python -r requirements-dev.txt",
    ".venv/bin/python -m pytest -q",
    ".venv/bin/python -m benchmarks.run --matrix ocr --tag new",
    ".venv/bin/python -m benchmarks.production models new",
    ".venv/bin/python -m benchmarks.production images new",
    ".venv/bin/python -m benchmarks.production heldout new",
    ".venv/bin/python -m benchmarks.final_serial",
    ".venv/bin/python -m benchmarks.adversarial",
    "```",
    "",
    "Live modules spend API credits. Save existing result files before rerunning modules that use fixed output names. Raw JSONL records, fixtures and summary.json are stored alongside this report.",
]
(OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
files = (
    list((ROOT / "beru").glob("*.py"))
    + list((ROOT / "benchmarks").glob("*.py"))
    + [
        ROOT / "scripts/ocr.swift",
        ROOT / "scripts/semantic_worker.py",
        ROOT / "requirements.txt",
        ROOT / "requirements-dev.txt",
    ]
)
manifest = {
    "python": platform.python_version(),
    "source_hashes": {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in files
    },
}
(OUT / "code-manifest.json").write_text(json.dumps(manifest, indent=2))
print(json.dumps(summary, indent=2))
