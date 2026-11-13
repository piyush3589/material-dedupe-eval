import csv
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "pairs.csv"


def load_pairs(path=DEFAULT_PATH):
    """Return a list of dicts: id, a, b, label (int 0/1), category, note."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["label"] = int(r["label"])
    return rows
