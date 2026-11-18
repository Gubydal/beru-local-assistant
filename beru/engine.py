"""Shared, testable OCR → question validation → retrieval → model pipeline."""

import hashlib, io, re, time, threading, os
from beru.knowledge import ROOT, search
from beru.ocr import read
from beru.question import Abstention
from beru.providers import answer, load_env, read_image


class Engine:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()

    def solve(
        self,
        image,
        provider="gemini",
        visual=False,
        model=None,
        on_read=None,
        use_cache=True,
        refresh=False,
    ):
        started = time.monotonic()
        vision_fallback = False
        try:
            question = read(image)
        except ValueError:
            if not visual:
                raise
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            question = read_image(buffer.getvalue(), provider, model)
            vision_fallback = True
        ocr_seconds = time.monotonic() - started
        if on_read:
            on_read(question)
        load_env()
        model = model or os.getenv(
            "GEMINI_MODEL" if provider == "gemini" else "DEEPSEEK_MODEL",
            "gemini-3.8-flash" if provider == "gemini" else "deepseek-flash",
        )
        payload = None
        if visual:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            payload = buffer.getvalue()
        corpus = ROOT / "knowledge/index.sqlite"
        if not corpus.exists():
            raise ValueError(
                "Knowledge index is missing; index your sources before answering."
            )
        cloud_path = ROOT / "knowledge/gemini-vectors.npz"
        retrieval_version = (
            str(cloud_path.stat().st_mtime_ns) if cloud_path.exists() else "local"
        )
        retrieval_version += os.getenv("BERU_CLOUD_RETRIEVAL", "1")
        key = hashlib.sha256(
            (
                question.fingerprint
                + provider
                + retrieval_version
                + model
                + (hashlib.sha256(payload).hexdigest() if payload else "")
                + str(corpus.stat().st_mtime_ns)
            ).encode()
        ).hexdigest()
        with self.lock:
            cached = self.cache.get(key) if use_cache and not refresh else None
        if cached:
            return {
                **cached,
                "cached": True,
                "total": time.monotonic() - started,
                "ocr_seconds": ocr_seconds,
            }
        t = time.monotonic()
        evidence = search(question.text)
        retrieval_seconds = time.monotonic() - t
        result = answer(question.text, evidence, provider, model, image=payload)
        if result["answer"].strip().upper() in ["NONE", "AUCUNE", "NO ANSWER"]:
            raise Abstention(
                "No supported answer among the visible choices; capture the complete question or inspect the sources."
            )
        match = re.match(r"^\s*([a-f])(?:[.\s):]|$)", result["answer"], re.I)
        if not match or match[1].lower() not in question.options:
            raise ValueError(
                "Model returned an option outside the visible choices; recapture or retry."
            )
        result.update(
            question=question.text,
            evidence=evidence,
            total=time.monotonic() - started,
            ocr_seconds=ocr_seconds,
            retrieval_seconds=retrieval_seconds,
            retrieval_mode=(
                evidence[0].get("retrieval_mode", "local_hybrid")
                if evidence
                else "none"
            ),
            ocr_confidence=question.confidence,
            question_box=question.box,
            model=model,
            vision_fallback=vision_fallback,
            cached=False,
        )
        if use_cache:
            with self.lock:
                if len(self.cache) >= 256:
                    self.cache.clear()
                prior = self.cache.get(key)
                if not prior or prior.get("_cache_started", 0) <= started:
                    self.cache[key] = dict(result, _cache_started=started)
        return result
