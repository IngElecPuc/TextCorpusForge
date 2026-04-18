from textforge.normalize.unicode_norm import normalize_unicode


def test_unicode_normalization_returns_text() -> None:
    assert isinstance(normalize_unicode("á"), str)
