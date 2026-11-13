import pytest

from dedupe.metrics import confusion, per_category_accuracy, scores


def test_confusion_counts():
    labels = [1, 1, 1, 0, 0, 0]
    preds = [1, 1, 0, 1, 0, 0]
    assert confusion(labels, preds) == (2, 1, 1, 2)


def test_scores_hand_calculated():
    s = scores([1, 1, 1, 0, 0, 0], [1, 1, 0, 1, 0, 0])
    assert s["precision"] == pytest.approx(2 / 3)
    assert s["recall"] == pytest.approx(2 / 3)
    assert s["f1"] == pytest.approx(2 / 3)
    assert s["accuracy"] == pytest.approx(4 / 6)


def test_scores_asymmetric_case_so_precision_and_recall_cannot_be_swapped():
    # tp=1, fn=3, fp=1, tn=1  ->  precision 1/2, recall 1/4, f1 1/3
    s = scores([1, 1, 1, 1, 0, 0], [1, 0, 0, 0, 1, 0])
    assert (s["tp"], s["fn"], s["fp"], s["tn"]) == (1, 3, 1, 1)
    assert s["precision"] == pytest.approx(1 / 2)
    assert s["recall"] == pytest.approx(1 / 4)
    assert s["f1"] == pytest.approx(1 / 3)


def test_all_wrong_does_not_divide_by_zero():
    s = scores([1, 0], [0, 1])
    assert s["precision"] == 0 and s["recall"] == 0 and s["f1"] == 0


def test_never_predicting_duplicate_gives_zero_recall():
    assert scores([1, 1, 0], [0, 0, 0])["recall"] == 0


def test_per_category_accuracy():
    rows = [
        {"category": "a", "label": 1, "pred": 1},
        {"category": "a", "label": 0, "pred": 1},
        {"category": "b", "label": 0, "pred": 0},
    ]
    assert per_category_accuracy(rows) == {"a": (1, 2), "b": (1, 1)}
