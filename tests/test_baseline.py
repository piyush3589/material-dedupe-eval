"""Regression gate for the rule-based baseline.

If someone changes the normaliser or the matching rule and quality drops, CI fails here.
"""
import pytest

from dedupe.dataset import load_pairs
from dedupe.matchers import RulesMatcher
from dedupe.metrics import per_category_accuracy
from dedupe.run import evaluate

ROWS, SCORES = evaluate(RulesMatcher(), load_pairs())
F1_GATE = 0.85  # measured 0.881 when written; leaves a little room, not a lot


def test_f1_does_not_regress():
    assert SCORES["f1"] >= F1_GATE, f"F1 fell to {SCORES['f1']:.3f}"


def test_no_unusable_answers():
    assert SCORES["unusable_answers"] == 0


@pytest.mark.parametrize("category", ["different_size", "different_rating", "different_part_number", "different_material"])
def test_numeric_differences_are_never_called_duplicates(category):
    """Calling a 6205 bearing and a 6305 bearing 'duplicates' would merge two different parts. Zero tolerance."""
    cats = per_category_accuracy(ROWS)
    correct, total = cats[category]
    assert correct == total, f"{category}: {total - correct} false alarm(s)"


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("BEARING BALL 6205-2RS SKF", "SKF BALL BEARING 6205 2RS", True),
        ("BEARING BALL 6205-2RS SKF", "BEARING BALL 6305-2RS SKF", False),
        ("BOLT HEX M12X60 SS304", "BOLT HEX M12X70 SS304", False),
    ],
)
def test_spot_checks(a, b, expected):
    assert RulesMatcher().predict(a, b).duplicate is expected


@pytest.mark.xfail(reason="known limitation: baseline cannot convert 2 IN to 50 MM (case P19)", strict=True)
def test_known_gap_unit_conversion():
    assert RulesMatcher().predict("VALVE BALL 2IN SS316 FLANGED 150#", "BALL VALVE 50MM STAINLESS STEEL 316 FLG CLASS 150").duplicate is True
