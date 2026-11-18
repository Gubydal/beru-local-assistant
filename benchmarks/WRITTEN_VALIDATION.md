# Written-answer mode validation

The production pipeline now supports explicit `mode="written"` and optional `topic="coi"`. The UI offers Written answer, COI focus (on by default), and Copy answer. MCQ mode continues to enforce complete visible choices; it never silently treats an incomplete MCQ as a written question. Mode and topic are part of answer-cache identity.

135 automated tests pass, including written prompt extraction, low-quality rejection, cache separation, provider policy, incomplete visual-extraction rejection and clipboard output without evidence/uncertainty labels. The offscreen UI was inspected; native browser typing is outside this feature. Users copy and paste manually.

Six live production OCR/retrieval/answer checks (three per model) covered Structure, Action versus Time, and listing all ten indicators. All answers were manually reviewed against the source and passed keyword checks; all cited evidence and returned no uncertainty flag.

| Model | Correct live checks | Median | Maximum |
|---|---:|---:|---:|
| Gemini 3.8 Flash | 3/3 | 6.32s | 8.16s |
| Gemini 4 Hydrogen | 3/3 | 4.81s | 5.59s |

Initial replies mixed English and French indicator names. The written-answer instruction was improved to use the question's language, with optional original aliases. One follow-up per model correctly listed all ten indicators in French and returned no uncertainty flag. This is a small source-grounded smoke test, not an accuracy guarantee or controlled model speed comparison.

Definitions from original DOC Support 3-2 page 6 are now paired with the verified wheel orientations from page 7 in each indicator's source section. Both retrieval indexes were rebuilt. Local detailed results remain under `research/written-smoke/`. To reproduce the main live checks, run `.venv/bin/python -m benchmarks.written_smoke` (uses your local API key).
