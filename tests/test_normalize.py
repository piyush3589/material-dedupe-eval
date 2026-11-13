import pytest

from dedupe.normalize import normalize


@pytest.mark.parametrize(
    "text, expected_tokens",
    [
        ("BRG BALL 6310", ["BEARING", "BALL", "6310"]),
        ("PIPE 50MM", ["PIPE", "50", "MM"]),
        ('HOSE 1/2"', ["HOSE", "1/2", "IN"]),
        ("GASKET 4IN 150#", ["GASKET", "4", "IN", "CLASS", "150"]),
        ("BOLT M12X60 SS304", ["BOLT", "M12", "X", "60", "STAINLESS", "STEEL", "304"]),
    ],
)
def test_normalize(text, expected_tokens):
    assert normalize(text) == expected_tokens


def test_case_and_whitespace_do_not_matter():
    assert normalize("  gasket   spiral ") == normalize("GASKET SPIRAL")
