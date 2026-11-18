"""Stable binding between vector IDs and their original evidence rows."""

import hashlib, json


def digest(rows):
    return hashlib.sha256(
        json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()
