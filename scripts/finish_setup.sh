#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
uv pip install --python .venv/bin/python -r requirements.txt
.media-venv/bin/python scripts/import_slides.py
HF_HUB_DISABLE_XET=1 .media-venv/bin/python scripts/transcribe_remaining.py
HF_HUB_DISABLE_XET=1 .media-venv/bin/python scripts/transcribe_local.py small
.venv/bin/python -m beru.knowledge
HF_HUB_DISABLE_XET=1 .media-venv/bin/python scripts/semantic_worker.py index
.venv/bin/python scripts/source_catalog.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/benchmark_models.py
