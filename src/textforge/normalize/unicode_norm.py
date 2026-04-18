from __future__ import annotations

import unicodedata


def normalize_unicode(text: str, form: str = "NFKC") -> str:
    return unicodedata.normalize(form, text)
