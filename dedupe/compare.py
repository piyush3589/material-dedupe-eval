"""Compare finished runs side by side (e.g. prompt v1 vs v2, or model A vs model B).

  python -m dedupe.compare reports/rules reports/llm-v1 reports/llm-v2
"""
import json
import sys
from pathlib import Path


def main(dirs):
    runs = [json.loads((Path(d) / "summary.json").read_text()) for d in dirs]
    print("| Run | Accuracy | Precision | Recall | F1 | False alarms | Missed duplicates |")
    print("|---|---|---|---|---|---|---|")
    for r in runs:
        print(f"| {r['matcher']} | {r['accuracy']:.3f} | {r['precision']:.3f} | {r['recall']:.3f} | "
              f"{r['f1']:.3f} | {r['fp']} | {r['fn']} |")


if __name__ == "__main__":
    main(sys.argv[1:])
