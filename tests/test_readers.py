from textforge.io.readers_txt import canonicalize_text


def test_canonicalize_text_normalizes_whitespace() -> None:
    assert canonicalize_text("hola\t\t mundo\r\n\r\n") == "hola mundo"
