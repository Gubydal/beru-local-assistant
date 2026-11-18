"""Report correctness, availability and uncertainty separately; never certify 100%."""

import json, math, statistics, pathlib

OUT = pathlib.Path("research/hard-audit")


def load(name):
    return [json.loads(l) for l in (OUT / name).read_text().splitlines()]


def metrics(rows):
    answered = [r for r in rows if "result" in r]
    times = sorted(r["total_seconds"] for r in rows)
    return dict(
        attempted=len(rows),
        answered=len(answered),
        correct=sum(r["correct"] for r in rows),
        wrong=sum(not r["correct"] for r in answered),
        abstentions=sum(r.get("abstained", False) for r in rows),
        operational_failures=sum(
            "error" in r and not r.get("abstained", False) for r in rows
        ),
        source_retrieved=sum(r.get("source_retrieved", False) for r in answered),
        expected_source_cited=sum(
            r.get("expected_source_cited", False) for r in answered
        ),
        median_seconds=statistics.median(times),
        p95_seconds=times[min(len(times) - 1, int(0.95 * len(times)))],
        max_seconds=max(times),
        over_15=sum(t > 15 for t in times),
    )


rows = load("final-serial.jsonl")
stats = metrics(rows)
n = stats["answered"]
errors = stats["wrong"]
z = 1.96
p = errors / n
den = 1 + z * z / n
mid = (p + z * z / (2 * n)) / den
half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
summary = {
    "date": "2026-11-18",
    "overall_readiness": "NOT_FULLY_READY_FOR_ENTIRE_COURSE",
    "final": stats,
    "observed_answer_error_rate": errors / n,
    "illustrative_wilson_95_interval": [max(0, mid - half), min(1, mid + half)],
    "real_assessment_error_rate": None,
    "statistical_limit": "Purposively selected course-derived cases, not independent random exam sampling. Interval is illustrative only and cannot guarantee a real-exam error bound.",
    "missing_resource": None,
    "initial": {
        mode: metrics(load(mode + ".jsonl"))
        for mode in ["core", "permutations", "images"]
    },
    "local_before_cloud": metrics(load("serial-before-cloud.jsonl")),
    "photo_examples_scored": False,
}
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
lines = [
    "# Hard-question and knowledge audit — 18 November 2026",
    "",
    "## Readiness verdict",
    "",
    "**Not certified 100% ready for the entire course.** The supplied material was repaired and the current hard benchmark passed, and the managerial handout has now been supplied and indexed. The exact newer Moodle resource versions are not verified, and no official answer key was supplied for the photographed questions. Network tails remain possible.",
    "",
    "## Final serial run — current retrieval and parser",
    "",
    "| Measure | Result |",
    "|---|---:|",
    f"| Source-answerable questions | {stats['correct']}/{stats['attempted']} correct |",
    f"| Incorrect returned answers | {stats['wrong']} |",
    f"| Abstentions / operational failures | {stats['abstentions']} / {stats['operational_failures']} |",
    f"| Expected primary source retrieved | {stats['source_retrieved']}/{stats['answered']} |",
    f"| Expected primary source cited | {stats['expected_source_cited']}/{stats['answered']} |",
    f"| Median / p95 / maximum | {stats['median_seconds']:.2f}s / {stats['p95_seconds']:.2f}s / {stats['max_seconds']:.2f}s |",
    f"| Runs over 15 seconds | {stats['over_15']} |",
    "",
    "The 40 unique cases cover the Yemen training adaptation, Morocco time-management testimony, organizational-culture typologies, components of organizational culture, Hall’s matrix and Hofstede distinctions. Correct positions are rotated. The renderer receives the question and choices, not an answer annotation; the production Engine is called with cache disabled. The benchmark is synthetic and source-anchored, not an instructor-validated real-exam sample.",
    "",
    "## Error margin — what can be claimed",
    "",
    f"Observed returned-answer error rate: **{errors}/{n} = {100 * errors / n:.1f}%** in this final set. That is not a true error rate of zero. Under an ideal independent representative Bernoulli-sample assumption, a two-sided 95% Wilson interval would be **{100 * max(0, mid - half):.1f}%–{100 * min(1, mid + half):.1f}%**. The purposive, topic-clustered, course-derived cases do not meet a random exam-sampling design, so this interval is illustrative rather than a guaranteed bound for Moodle.",
    "",
    "Approximately 299 independent representative verified questions with zero errors would be needed for a one-sided 95% binomial upper bound below 1%; even that would not certify 100% correctness or API availability. Wrong answers, abstentions, capture failures and timeouts must remain separate metrics.",
    "",
    "## Resource coverage",
    "",
    "| Moodle label | Local match | Status |",
    "|---|---|---|",
    "| SUP_Managerial behavior – Cultural aspects | DOC Support 6-1 | Four pages visually reviewed and indexed |",
    "| CAS_Biais Culturel_Formation (Yemen) | DOC Support 6-2 | Matching case content indexed |",
    "| VID_Biais culturel de la Gestion du Temps (Maroc) | YouTube 9QdyxU7tseo transcript | Matching testimony indexed; automatic transcript |",
    "| SUP_Organizational Culture | DOC Support 5-1 | Matching handout indexed; diagrams repaired |",
    "",
    "These are matches by content, not a checksum comparison against newly downloaded Moodle files. knowledge/sources.json records source roles/hashes and missing mappings. knowledge-audit.json found no unindexed source files or unexpected indexed Markdown. The corpus has 37 sources and 431 passages. Generated analysis notes and this benchmark remain outside the evidence corpus.",
    "",
    "## Real defects found and repaired",
    "",
    "- Image-based material was missing from the text index. Visually inspected the original PDF pages and transcribed Hall’s page-2 matrix, organizational components on page 3, Cameron–Quinn’s page-6 quadrants and selected appendix rows on page 7. Column relationships were preserved rather than blindly merging OCR text.",
    "- OCR emitted Cyrillic/Greek lookalikes for Latin option labels and merged a radio circle with B as “Ob.”. The marker parser now normalizes those prefixes without rewriting the question or answer-changing words. Added regression tests.",
    "- The previous retrieval often answered correctly from weaker material: in a 40-case serial run it retrieved/cited the expected source in only 33 cases. Added Gemini embedding retrieval with locally stored document vectors, corpus-digest validation, bounded query requests and local fallback. Expected-source retrieval/citation reached 40/40 in the final run.",
    "- Both retrieval indexes are invalidated on corpus rebuild. Answer-cache identity now includes the stronger retrieval index version and retrieval-mode switch. Unit tests disable paid cloud retrieval unless explicitly mocking it.",
    "- A visibly garbled mixed-language automatic transcript was flagged. Its clear English portions are useful, but they cannot certify all course terminology or oral explanations.",
    "",
    "Building the stronger index sent the source passages to the configured Google API. Normal use sends the question for an embedding, then the question plus retrieved evidence to the selected answer model. Vectors remain local. Set BERU_CLOUD_RETRIEVAL=0 to disable cloud query retrieval; that reverts to the lower-recall local path.",
    "",
    "## Earlier stress outcomes — retained, not hidden",
    "",
    "| Earlier suite | Correct | Failed runs | Returned wrong answers | p95 |",
    "|---|---:|---:|---:|---:|",
]
for mode in ["core", "permutations", "images"]:
    m = summary["initial"][mode]
    lines.append(
        f"| {mode} | {m['correct']}/{m['attempted']} | {m['attempted'] - m['answered']} | {m['wrong']} | {m['p95_seconds']:.2f}s |"
    )
lines += [
    "",
    "The initial core failures were capture/parser rejections, not wrong semantic choices. The shuffled stress run had two 35-second API read timeouts while multiple test processes were active. An early failure-only retest also produced one abstention and another timeout. A previous valid local-retrieval serial response took 22.48 seconds. The final run was faster, but these observations prevent a hard 15-second or availability guarantee. Failure-only retests are regression evidence, not independent new accuracy samples.",
    "",
    "## New photographed examples — deliberately unscored",
    "",
    "| Reconstructed wording | Current responses | Why not an accuracy score |",
    "|---|---|---|",
]
probes = load("photo-probes.jsonl")
for id, title in [
    (
        "photo_hofstede_comparison",
        "Hofstede: comparison across societies / across periods",
    ),
    ("photo_school_mental_map", "School education and “Carte du Monde”"),
    ("photo_implicit_rules", "Internalized rules: low versus high context"),
]:
    rs = [r for r in probes if r["id"] == id]
    answers = "; ".join(
        r.get("result", {}).get("answer", r.get("error", "")) for r in rs
    )
    lines.append(
        f"| {title} | {answers} | No instructor key; selected radio is not gold truth |"
    )
lines += [
    "",
    "Original photo bytes were not available to the local harness; wording and Moodle-style cards were reconstructed. Before the retrieval upgrade, the school/mental-map probe alternated between NON and OUI across renderings. The upgraded run answered OUI in both variants, but consistency is not proof of the instructor’s expected answer. The exact phrase “Carte du Monde” is not established in the clear source passages; the newly supplied managerial handout does not establish that exact phrase. The broad Hofstede comparison question can also depend on what the course means by cross-sectional versus longitudinal use.",
    "",
    "## Artifacts and reproduction",
    "",
    "- hard_cases.py defines the frozen source-anchored cases; each has an evidence anchor checked against the supplied corpus.",
    "- final-serial.jsonl contains current end-to-end outcomes and cited passages. core.jsonl, permutations.jsonl, images.jsonl and serial-before-cloud.jsonl retain earlier runs.",
    "- cloud-retrieval-ablation.json and integrated-retrieval.json isolate expected-source retrieval rather than relying only on answer correctness.",
    "- photo-probes-before-cloud.jsonl and photo-probes.jsonl preserve the unscored example comparison.",
    "- knowledge-audit.json and knowledge/sources.json record provenance and missing coverage. The rendered original PDF pages are stored alongside this report for audit.",
    "",
    "```sh",
    ".venv/bin/python -m pytest -q",
    ".venv/bin/python scripts/audit_knowledge.py",
    ".venv/bin/python -m benchmarks.hard_retest",
    ".venv/bin/python -m benchmarks.new_example_probes",
    ".venv/bin/python -m benchmarks.hard_report",
    "```",
    "",
    "Live benchmark commands spend API credits and overwrite their fixed-name result files; archive earlier outcomes before rerunning. Error intervals are conditional descriptions, not a promise of exam accuracy.",
]
(OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
print(json.dumps(summary, ensure_ascii=False, indent=2))

if (OUT / 'managerial-results.jsonl').exists():
    managerial = load('managerial-results.jsonl')
    m = metrics(managerial)
    summary['managerial_followup'] = m
    summary['managerial_followup']['design'] = '12 new unique scenarios, 6 JPEG repeats, 8 previous regression questions; do not count all 26 as independent new questions.'
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    with (OUT / 'REPORT.md').open('a') as f:
        f.write('\n## Supplied managerial handout — follow-up\n\n')
        f.write('DOC Support 6-1.pdf has been supplied, OCR-extracted and visually checked on all four pages. All four requested resource labels now have indexed content matches. Both semantic indexes were rebuilt: 37 sources, 431 passages.\n\n')
        f.write(f"Production Engine, Gemini 3.8 Flash, cache disabled: {m['correct']}/{m['attempted']} correct; expected source retrieved {m['source_retrieved']}/{m['attempted']}, cited {m['expected_source_cited']}/{m['attempted']}. Median {m['median_seconds']:.2f}s, p95 {m['p95_seconds']:.2f}s, maximum {m['max_seconds']:.2f}s; {m['over_15']} over 15s.\n\n")
        f.write('Design: 12 new source-checked managerial scenarios, six JPEG repeats, eight earlier regression questions. Questions cover hierarchy versus consensus, contextual communication versus direct feedback, unanimity, persuasion, trust, disagreement and time. Repeats are not independent evidence. Gold answers were fixed against the PDF before evaluation. No official photo answer key exists. 124 automated checks pass. Real-assessment error remains unknown; the earlier illustrative interval is not a guarantee.\n\nRaw results: managerial-results.jsonl. Reproduce with `.venv/bin/python -m benchmarks.managerial_audit`.\n')

if (OUT / 'coi-results.jsonl').exists():
    coi = metrics(load('coi-results.jsonl'))
    summary['coi_table_followup'] = coi
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    with (OUT / 'REPORT.md').open('a') as f:
        f.write('\n## COI table and manual practice expansion\n\n')
        f.write('All four priority resources are indexed. The user-provided COI slide table was visually transcribed with explicit photo provenance into DOC Support 3-2.md. It distinguishes cultural due diligence, style switching, cultural dialogue and cultural mentoring. Corpus: 37 sources / 431 passages; both semantic indexes rebuilt.\n\n')
        f.write('Two additional selectable practice tests contain 24 fundamentals and 28 deep scenarios, retaining the original 29-question test. All 52 added questions have source anchors. Browser checks verified every question, scoring, corrections, separate persistence, switching and mobile layout. 125 automated checks pass.\n\n')
        f.write(f"Live production Engine COI scenarios: {coi['correct']}/{coi['attempted']} correct; source retrieved {coi['source_retrieved']}/{coi['attempted']}, cited {coi['expected_source_cited']}/{coi['attempted']}; median {coi['median_seconds']:.2f}s, maximum {coi['max_seconds']:.2f}s. These are source-derived synthetic questions, not official exam validation. Raw: coi-results.jsonl.\n")
