"""Run one matcher over the labelled pairs and write a report.

  python -m dedupe.run --matcher rules --out reports/rules
  ANTHROPIC_API_KEY=... python -m dedupe.run --matcher llm --prompt v2 --out reports/llm-v2
"""
import argparse
import csv
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .dataset import DEFAULT_PATH, load_pairs
from .matchers import LLMMatcher, RulesMatcher
from .metrics import per_category_accuracy, scores


def evaluate(matcher, pairs, workers=1):
    """Score a matcher. workers > 1 asks several pairs at once (useful for slow LLM calls); order is kept."""
    if workers > 1:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            preds = list(ex.map(lambda p: matcher.predict(p["a"], p["b"]), pairs))
    else:
        preds = [matcher.predict(p["a"], p["b"]) for p in pairs]
    rows = []
    for p, pred in zip(pairs, preds):
        # An unusable answer counts as "not a duplicate" but is tracked separately.
        rows.append({**p, "pred": int(bool(pred.duplicate)), "failed": pred.duplicate is None, "reason": pred.reason})
    s = scores([r["label"] for r in rows], [r["pred"] for r in rows])
    s["unusable_answers"] = sum(r["failed"] for r in rows)
    s["pairs"] = len(rows)
    return rows, s


def write_report(out_dir, matcher_name, rows, s):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "category", "label", "pred", "correct", "a", "b", "reason"])
        for r in rows:
            w.writerow([r["id"], r["category"], r["label"], r["pred"], int(r["label"] == r["pred"]), r["a"], r["b"], r["reason"]])
    (out / "summary.json").write_text(json.dumps({"matcher": matcher_name, **s}, indent=2), encoding="utf-8")

    cats = per_category_accuracy(rows)
    fails = [r for r in rows if r["label"] != r["pred"]]
    md = [f"# Evaluation report: {matcher_name}", "",
          f"Pairs: {s['pairs']}  |  unusable answers: {s['unusable_answers']}", ""]
    if s["unusable_answers"]:
        md += [f"> **WARNING: {s['unusable_answers']} of {s['pairs']} answers were unusable (API errors or unreadable replies).** "
               "They are scored as 'not duplicate', which makes the numbers below misleading. Fix the cause first; "
               "the reason column of the table at the bottom shows it.", ""]
    md += [
          "| Metric | Value |", "|---|---|",
          f"| Accuracy | {s['accuracy']:.3f} |", f"| Precision | {s['precision']:.3f} |",
          f"| Recall | {s['recall']:.3f} |", f"| F1 | {s['f1']:.3f} |", "",
          "| | Predicted duplicate | Predicted not duplicate |", "|---|---|---|",
          f"| **Actually duplicate** | {s['tp']} | {s['fn']} |",
          f"| **Actually different** | {s['fp']} | {s['tn']} |", "",
          "## Accuracy by category", "", "| Category | Correct | Total |", "|---|---|---|"]
    md += [f"| {c} | {k} | {n} |" for c, (k, n) in cats.items()]
    md += ["", f"## Wrong answers ({len(fails)})", "",
           "| ID | Type | Expected | A | B | Why the matcher said so |", "|---|---|---|---|---|---|"]
    for r in fails:
        kind = "missed duplicate" if r["label"] == 1 else "false alarm"
        md.append(f"| {r['id']} | {kind} | {'duplicate' if r['label'] else 'different'} | {r['a']} | {r['b']} | {r['reason']} |")
    (out / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--matcher", choices=["rules", "llm"], required=True)
    ap.add_argument("--data", default=str(DEFAULT_PATH))
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt", default="v2", choices=["v1", "v2"])
    ap.add_argument("--provider", default="anthropic", choices=["anthropic", "groq"])
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL"))
    ap.add_argument("--workers", type=int, default=None, help="parallel LLM calls (default 4 for llm, 1 for rules)")
    a = ap.parse_args(argv)

    if a.matcher == "rules":
        matcher = RulesMatcher()
    else:
        if not a.model:
            ap.error("--model (or env LLM_MODEL) is required for the llm matcher")
        matcher = LLMMatcher(a.model, a.prompt, a.provider)
    workers = a.workers if a.workers is not None else (4 if a.matcher == "llm" else 1)
    rows, s = evaluate(matcher, load_pairs(a.data), workers=workers)
    write_report(a.out, matcher.name, rows, s)
    print(f"{matcher.name}: accuracy={s['accuracy']:.3f} precision={s['precision']:.3f} "
          f"recall={s['recall']:.3f} f1={s['f1']:.3f} unusable={s['unusable_answers']}  -> {a.out}/report.md")
    if s["unusable_answers"]:
        first = next(r["reason"] for r in rows if r["failed"])
        print(f"\nWARNING: {s['unusable_answers']} of {s['pairs']} answers were unusable, so these scores are NOT meaningful.\n"
              f"First problem: {first}")
        if s["unusable_answers"] == s["pairs"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
