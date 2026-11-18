# Beru local prototype

A macOS always-on-top MCQ assistant with region selection, automatic change detection, local Apple Vision OCR (English/French), local document search, and Gemini/DeepSeek API answering. Answer-only view is default; evidence can be expanded.

## Repository contents and private data

This repository includes application source, the local practice website, scripts and tests. API credentials, original course documents/transcripts, generated knowledge indexes, screenshots, live API responses, cloned reference projects and virtual environments are excluded. The course-specific practice questions are included; they are generated exercises, not an official exam answer key.

Copy `API.env.example` to `API.env` and fill in your own provider key locally. Add your own Markdown sources under `knowledge/documents/`, `knowledge/videos/` or `knowledge/web/`, then build the index. A fresh clone has no private knowledge corpus. Corpus-specific audits and benchmarks require the original local sources; they will not reproduce from the code alone.

## Run

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
mkdir -p bin
swiftc scripts/ocr.swift -o bin/beru-ocr
.venv/bin/python -m beru.knowledge
.venv/bin/python -m beru.app
```

Grant Screen Recording permission to the terminal/application when macOS requests it. Select a question area using the centered adjustable frame and confirm with Use area, keep the overlay outside it, and press Watch / pause. Capture triggers manually. Select all options; scrolling questions are not assembled automatically.

In API.env, configure GEMINI_API_KEY or DEEPSEEK_API_KEY. Optional GEMINI_MODEL and DEEPSEEK_MODEL override defaults. API.env is ignored by git. Provider keys remain in the Python process; only the question and retrieved excerpts go to the provider.

## Current limits

This is an initial prototype, not an accuracy-validated product. Retrieval uses SQLite FTS5 keyword ranking and optional multilingual vector retrieval with reciprocal rank fusion; cross-encoder reranking is pending. Gemini 3.8 Flash is the provisional default. Two-question smoke tests passed on 3.5 Flash-Lite, 3.8 Flash and 4 Argon, which is insufficient to establish an accuracy winner. Answers include model-reported uncertainty, which is not a calibrated probability. Total latency is shown after each answer; there is no 15-second guarantee. In-flight provider calls may take up to 35 seconds and obsolete results are discarded. Global shortcuts, packaging, persistent settings, semantic answer caching, and automated scrolling are not implemented.

Sources are retained in knowledge/ as page-referenced Markdown and timestamped transcripts. knowledge/manifest.json records the initial extraction; recovery output may supersede that initial status. Missing transcripts/scanned pages must be checked before treating the corpus as complete.

No third-party repository code has been copied into the prototype. Clones under research/repos are reference material and excluded from git.

## Optional local semantic retrieval

Double-click Beru.command to launch the installed prototype. Use “Include image for diagrams” when visual content is essential; this sends the screenshot alongside the extracted text in the same model request.

A separate Python 3.12 environment avoids media/model wheel incompatibilities with the system Python 3.14:

```sh
uv venv --python 3.12 .media-venv
uv pip install --python .media-venv/bin/python -r requirements-media.txt
.media-venv/bin/python scripts/semantic_worker.py index
```

This downloads a multilingual Model2Vec model and builds a local vector index. The app loads the model once in a background worker, combines vector and keyword ranks, and discounts the two derivative guides. Until the worker is ready, it falls back to keyword retrieval. Rebuilding the keyword index invalidates the vector index; rebuild vectors afterward. Cross-encoder reranking is not yet implemented.

Run `scripts/benchmark_models.py` after saving API credentials. It tests a small model smoke-test set and records research/model-benchmark.json; it does not establish a statistically meaningful accuracy ranking.

Exact recognized question text is cached in memory for the current application session, scoped to provider and corpus modification time. This avoids repeated API calls when the same question is captured again. Clear/restart the app after changing a model configuration. Keeping the question panel outside the selected area prevents the assistant's own output from retriggering capture.

## Expanded validation and behavior

Run `uv pip install --python .venv/bin/python -r requirements-dev.txt` and `.venv/bin/python -m pytest -q` for deterministic/offscreen regression checks. The suite uses pytest-qt. Live evaluations in `benchmarks/` use paid API calls and save their raw outcomes under `research/benchmark/`; they are intentionally not part of pytest.

The app now validates the visible question and option labels before answering, filters Moodle navigation/timers, handles missing OCR punctuation on radio choices, and retries failed local OCR once with image preprocessing. Unreadable or incomplete captures are rejected. Missing whole choices cannot always be detected from a crop; select the entire question card. “Include image” permits visual recovery when local OCR fails, potentially adding a second cloud call and extra latency. It remains off by default.

The model selector defaults to Gemini 3.8 Flash. Gemini 4 Argon is slower in these tests; Flash-Lite made subtle semantic errors. Capture explicitly refreshes the current answer; automatic monitoring can reuse a cached answer. Pause discards queued work, stale answers are not shown, and one newer request can bypass one slower obsolete request. Network/API calls still have finite timeouts rather than a hard end-to-end 15-second guarantee.

No browser extension or site integration was added. Normal OS screen capture and manual interaction remain the workflow. No claim of undetectability is made.

The expanded evaluation report is `research/benchmark/REPORT.md`. Its latest run has 107 passing checks with 87.4% Python statement coverage. The fresh source-answerable synthetic cohort scored 46/46, with median 3.89s and p95 6.05s; this is not a guarantee for real assessment pages. Exact input photos and physical browser interaction remain unverified. Manual Capture pauses automatic monitoring; resume with Watch / pause after a manual answer.

For coverage, run `.venv/bin/python -m pytest --cov=beru --cov-report=term-missing -q`. Python coverage does not measure Swift/Vision internals or prove native screen-capture behavior.

## Moodle-style practice platform and floating window

1. Double-click `Practice.command` to start the local quiz and open your browser. It is currently served at http://127.0.0.1:8765/. Keep its terminal open while using the page. Reopening the launcher reuses the existing server; if another application occupies that port, a nearby port is selected and printed.
2. Close any old Beru window and double-click `Beru.command` again to load the updated floating-panel behavior. Beru now uses a macOS tool panel, stays visible when inactive, joins Spaces/fullscreen applications, and uses native window level 25. It does not repeatedly activate itself or take browser keyboard focus.
3. Enable Screen Recording for the launching Terminal/Python application in System Settings → Privacy & Security → Screen & System Audio Recording (called Screen Recording on some versions). Restart Beru/Terminal if macOS requests it.
4. In the quiz, click Recommencer if you want a fresh attempt. In Beru, click Select area. A centered frame appears: drag it over the entire blue question card, resize with the bottom-right grip, then click Use area or press Enter. Move the Beru panel outside that selected region.
5. Click Watch / pause. Choose the answer yourself in the browser, then Page suivante; the changed question is detected automatically. Capture forces a fresh manual answer and pauses monitoring; click Watch / pause to resume.
6. Terminer le test reveals the expected answers and source references. Answers, flags, timer and current question are saved only in this browser's local storage. No Moodle login or connection is used.

The practice page includes 29 questions, previous/next navigation, question flags, answer clearing, a configurable timer, resume after reload and a scored correction view. The server exposes only the practice folder, not the workspace or API.env.

Validation for this change: real-browser checks passed for navigation, selection, clearing, flags, reload persistence, scoring, reset, timer expiration, laptop/mobile layout and server isolation. A native Cocoa check observed Beru remaining visible at level 25 while its application was inactive after opening the browser. A screenshot of the actual browser-rendered first question passed the production OCR/retrieval/Gemini pipeline in 5.46 seconds. Fullscreen collection flags are configured; physical browser fullscreen/Spaces behavior still merits testing on your display arrangement.

## Stronger multilingual retrieval (November 18 audit)

The current corpus includes visually checked transcriptions of image-based Hall and organizational-culture diagrams. `knowledge/sources.json` records source roles, hashes, and matches to the requested course resource names; `research/hard-audit/knowledge-audit.json` records missing coverage.

A local vector file built from Google `gemini-embedding-001` passages now supplies the stronger retrieval ranking when available. Building it sends the document passages to Google once; normal use sends the question for its query embedding. Vectors stay local. A bounded request timeout falls back to local Model2Vec/keyword retrieval. To rebuild after changing the corpus:

```sh
.venv/bin/python -m beru.knowledge
.media-venv/bin/python scripts/semantic_worker.py index
.venv/bin/python scripts/build_cloud_index.py
.venv/bin/python scripts/audit_knowledge.py
```

Set `BERU_CLOUD_RETRIEVAL=0` in the launch environment to keep retrieval local. Google query embeddings require the existing Gemini key; answer generation still uses the selected model. Restart Beru after code changes to load the upgraded retrieval implementation.


Practice now offers three tests in the **Test** menu: original (29), fundamentals (24), and deep scenarios (28). The two added tests focus on organizational culture, managerial behavior, the Yemen case, Morocco time-management testimony, and the COI skills table. Direct URLs: `http://127.0.0.1:8765/?test=fundamentals` and `http://127.0.0.1:8765/?test=deep`. Each test saves separate progress; corrections and source references appear after finishing. Practice gold answers are course-derived, not an official instructor key. Generated questions stay outside the retrieval corpus.
