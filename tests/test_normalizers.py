from textforge.normalize.line_cleanup import canonicalize_segment


def test_canonicalize_segment():
    assert canonicalize_segment(' Hola  mundo  ') == 'Hola mundo'
