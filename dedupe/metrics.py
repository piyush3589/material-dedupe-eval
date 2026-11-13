from collections import defaultdict


def confusion(labels, preds):
    """labels/preds are 0/1. Returns tp, fp, fn, tn."""
    tp = sum(1 for l, p in zip(labels, preds) if l == 1 and p == 1)
    fp = sum(1 for l, p in zip(labels, preds) if l == 0 and p == 1)
    fn = sum(1 for l, p in zip(labels, preds) if l == 1 and p == 0)
    tn = sum(1 for l, p in zip(labels, preds) if l == 0 and p == 0)
    return tp, fp, fn, tn


def _div(a, b):
    return a / b if b else 0.0


def scores(labels, preds):
    tp, fp, fn, tn = confusion(labels, preds)
    precision = _div(tp, tp + fp)
    recall = _div(tp, tp + fn)
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "accuracy": _div(tp + tn, tp + fp + fn + tn),
        "precision": precision,
        "recall": recall,
        "f1": _div(2 * precision * recall, precision + recall),
    }


def per_category_accuracy(rows):
    """rows: dicts with category, label, pred. Returns {category: (correct, total)}."""
    acc = defaultdict(lambda: [0, 0])
    for r in rows:
        acc[r["category"]][1] += 1
        acc[r["category"]][0] += int(r["label"] == r["pred"])
    return {k: tuple(v) for k, v in sorted(acc.items())}
