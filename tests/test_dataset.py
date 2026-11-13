"""Quality checks on every labelled file. A bad dataset makes every score meaningless."""
import re
from pathlib import Path

import pytest

from dedupe.dataset import load_pairs

DATA = Path(__file__).resolve().parent.parent / "data"
FILES = ["pairs.csv", "pairs_hard.csv", "pairs_heldout.csv"]
ALL = {f: load_pairs(DATA / f) for f in FILES}


@pytest.fixture(params=FILES)
def pairs(request):
    return ALL[request.param]


def test_ids_are_unique_within_and_across_files():
    ids = [p["id"] for rows in ALL.values() for p in rows]
    assert len(ids) == len(set(ids))


def test_labels_are_binary(pairs):
    assert {p["label"] for p in pairs} <= {0, 1}


def test_classes_are_reasonably_balanced(pairs):
    pos = sum(p["label"] for p in pairs)
    assert 0.4 <= pos / len(pairs) <= 0.6, "dataset is too skewed: accuracy would be misleading"


def test_no_empty_descriptions(pairs):
    assert all(p["a"].strip() and p["b"].strip() for p in pairs)


def test_no_pair_appears_twice_in_any_file_or_order():
    seen = {}
    for f, rows in ALL.items():
        for p in rows:
            key = frozenset([p["a"].strip().upper(), p["b"].strip().upper()])
            assert key not in seen, f"{p['id']} ({f}) repeats {seen[key]}"
            seen[key] = p["id"]


def test_every_row_has_category_and_note(pairs):
    assert all(p["category"] and p["note"] for p in pairs)


def test_negatives_are_not_textually_identical(pairs):
    for p in pairs:
        if p["label"] == 0:
            assert p["a"].strip().upper() != p["b"].strip().upper(), p["id"]


def test_id_suffix_matches_label(pairs):
    """P01 / HP01 / XP01 are duplicates; N01 / HN01 / XN01 are different items."""
    for p in pairs:
        kind = re.search(r"([PN])\d+$", p["id"])
        assert kind, f"unexpected id format {p['id']}"
        assert p["label"] == (1 if kind.group(1) == "P" else 0), p["id"]


def test_hard_set_is_not_a_copy_of_the_easy_set():
    easy = {frozenset([p["a"].strip().upper(), p["b"].strip().upper()]) for p in ALL["pairs.csv"]}
    for f in ("pairs_hard.csv", "pairs_heldout.csv"):
        for p in ALL[f]:
            assert frozenset([p["a"].strip().upper(), p["b"].strip().upper()]) not in easy
