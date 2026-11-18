"""Conservative extraction of a single visible MCQ, excluding Moodle chrome."""

import re, hashlib, unicodedata
from dataclasses import dataclass

NOISE = re.compile(
    r"^(?:moodl[ei]|management interculturel\s*&|question\s*\d|navigation du test|temps restant|page (?:suivante|précédente)|effacer mon choix|pas encore|noté sur|marquer la question|terminer le test|tableau de bord|mes cours|tous les cours|recherche de cours|français\s*\()",
    re.I,
)
OPTION = re.compile(r"^\s*[^\w\n]*\s*(?:[oO0]\s*)?([a-fA-F])[.)]\s*(.+)$")


class Abstention(ValueError):
    """No defensible answer among the visible choices."""


@dataclass
class Question:
    text: str
    options: dict
    confidence: float
    box: tuple | None = None

    @property
    def fingerprint(self):
        # Keep negations, labels, diacritics and answer-changing words. Only normalize typography.
        value = unicodedata.normalize("NFKC", self.text).replace("’", "'")
        return hashlib.sha256(" ".join(value.casefold().split()).encode()).hexdigest()


def parse(lines):
    clean = [
        line
        for line in lines
        if line.get("text", "").strip() and not NOISE.search(line["text"].strip())
    ]
    stem = []
    options = {}
    used = []
    current = None
    for line in clean:
        value = line["text"].strip()
        # Vision occasionally emits Cyrillic/Greek glyphs for Latin option labels.
        # Normalize the marker only; never rewrite answer-changing words in the text.
        confusables = {
            "а": "a",
            "А": "A",
            "ɑ": "a",
            "Α": "A",
            "α": "a",
            "В": "B",
            "Β": "B",
            "с": "c",
            "С": "C",
            "е": "e",
            "Е": "E",
            "Ε": "E",
        }
        value = re.sub(
            r"^(\s*[^\w]*(?:[oO0]\s*)?)([аАɑΑαВΒсСеЕΕ])(?=[.)\s])",
            lambda m: m[1] + confusables[m[2]],
            value,
        )
        match = OPTION.match(value) or re.match(
            r"^\s*(?:[•○●©°®◦]\s*|[oO0]\s*)([a-fA-F])\s+(.+)$", value
        )
        if match:
            label = match[1].lower()
            if label in options:
                raise ValueError(
                    "More than one question or duplicate option labels; select one complete question."
                )
            options[label] = match[2]
            current = label
            used.append(line)
        elif current:
            options[current] += " " + value
            used.append(line)
        else:
            stem.append(value)
            used.append(line)
    if len(options) < 2:
        raise ValueError(
            "Incomplete question: capture the stem and at least two fully visible options."
        )
    if list(options) != list("abcdef"[: len(options)]):
        raise ValueError(
            "Missing or unreadable option labels; capture all options from a onwards."
        )
    if not stem or len(" ".join(stem)) < 12:
        raise ValueError("Question stem is missing or unreadable.")
    confidence = min((float(l.get("confidence", 1)) for l in used), default=0)
    if confidence < 0.35:
        raise ValueError(
            "OCR confidence is too low; enlarge or recapture the question."
        )
    boxes = [l["box"] for l in used if l.get("box")]
    box = None
    if boxes:
        x = min(b[0] for b in boxes)
        y = min(b[1] for b in boxes)
        right = max(b[0] + b[2] for b in boxes)
        bottom = max(b[1] + b[3] for b in boxes)
        box = (
            max(0, x - 0.015),
            max(0, y - 0.02),
            min(1, right + 0.025),
            min(1, bottom + 0.03),
        )
    return Question(
        " ".join(stem) + "\n" + "\n".join(f"{k}. {v}" for k, v in options.items()),
        options,
        confidence,
        box,
    )


def from_text(text):
    return parse([{"text": line, "confidence": 1} for line in text.splitlines()])
