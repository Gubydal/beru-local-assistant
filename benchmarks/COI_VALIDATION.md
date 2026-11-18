# COI validation — 18 November 2026

Production OCR → retrieval → answering, answer cache disabled. Ten source-derived scenarios cover all ten COI indicators; each model also sees reversed choices, a wrongly selected radio and JPEG compression. There are ten unique questions, not forty independent questions.

| Model | Initial full-run correctness | COI evidence cited | Median per question | Maximum | Ten-question run durations |
|---|---:|---:|---:|---:|---:|
| Gemini 3.8 Flash | 20/20 | 20/20 | 4.53s | 6.87s | 47.73s / 45.93s |
| Gemini 4 Hydrogen | 20/20 | 20/20 | 5.63s | 12.48s | 62.32s / 62.30s |

All four automated ten-question runs were below 180 seconds. Timings exclude native screen capture and human reading, choice selection and navigation. Models ran sequentially and query-embedding caches may warm; these timing comparisons are descriptive. This small purposive test does not establish a real-exam accuracy rate or guarantee network latency.

Hydrogen flagged uncertainty on two correct Action/Being–Doing answers. Its retrieved context lacked the wheel details. Visually verified original DOC Support 3-2.pdf page 7, transcribed all ten wheel mappings into the primary source, and rebuilt retrieval. All ten explicit original mappings now retrieve. Retesting both Action variants with Hydrogen gave 2/2 correct, no uncertainty flags and citations to the original wheel (3.60s / 3.03s). The full forty-case run predates this repair and was preserved rather than relabeled as a post-repair run.

To receive the repaired source on another installation:

```sh
git pull
.venv/bin/python scripts/setup_knowledge.py --cloud
```

Restart Beru afterward. Credentials remain local. Run `.venv/bin/python -m benchmarks.coi_exam` to repeat the full test with your API key; it makes forty answer requests and records timestamped local reports under `research/coi-exam/`.
