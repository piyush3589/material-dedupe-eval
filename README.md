# Duplicate Material Detection: Evaluation Suite

A test harness that measures how well a matcher decides whether two spare-part (MRO) descriptions
refer to the same item. It scores any matcher the same way, so a rule-based baseline and an LLM can be
compared on identical data, and a change to a prompt, a model or a rule can be checked for regressions.

Material master data is full of near-duplicates such as `BEARING, BALL, 6205-2RS, SKF` and
`SKF BALL BEARING 6205 2RS`. Merging two records that are really different parts (a 6205 and a 6305
bearing) is far more costly than missing a duplicate, so the suite reports false alarms and missed
duplicates separately instead of a single accuracy number.

## At a glance

| | |
|---|---|
| Labelled pairs | 96 in three files: 60 easy, 24 hard (dev), 12 hard held-out |
| Categories | 12 (word order, abbreviations, unit notation, part-number formatting, different size / rating / type / material / part number / manufacturer, unit conversion) |
| Matchers included | Rule-based baseline, LLM matcher (Anthropic or Groq, with answer caching) |
| Metrics | Accuracy, precision, recall, F1, confusion matrix, per-category accuracy, list of wrong answers with reasons |
| Tests | 59 passing + 1 expected failure documenting a known gap, no API key needed |
| Stack | Python 3.9+, pytest, requests |

## Baseline results

The rule-based baseline normalises text, expands common abbreviations, and requires every number-bearing
token of one description to appear in the other.

| Metric | Value |
|---|---|
| Accuracy | 0.883 |
| Precision | 0.897 |
| Recall | 0.867 |
| F1 | 0.881 |
| False alarms (different items called duplicates) | 3 |
| Missed duplicates | 4 |

Full output: [`reports/rules/report.md`](reports/rules/report.md).

### Where the baseline goes wrong

| ID | Kind | Pair | Cause |
|---|---|---|---|
| P19 | missed duplicate | `VALVE BALL 2IN SS316 ...` vs `BALL VALVE 50MM STAINLESS STEEL 316 ...` | no unit conversion (2 IN = 50 MM) |
| P10 | missed duplicate | `V-BELT B68` vs `VBELT B-68` | the hyphen splits `B-68` into a stray letter token, which lowers word overlap below the threshold |
| P15 | missed duplicate | `OIL FILTER CAT 1R-0750` vs `CATERPILLAR OIL FILTER 1R0750` | `CAT` is not recognised as Caterpillar, so word overlap falls below the threshold |
| P17 | missed duplicate | `... GR8` vs `... GRADE 8` | `GR8` and `GRADE 8` are not recognised as the same grade |
| N05, N27, N29 | false alarm | gate vs globe valve, Y-type vs basket strainer, flat vs spring washer | the type word is one word among many, so word overlap stays above the threshold |

These are the cases an LLM matcher is expected to improve on, and the cases where it must be watched for
the opposite mistake: over-merging items that differ in one decisive word.

### The easy set was too easy: a harder set was added

On the first 60 pairs a general-purpose LLM scored a perfect 1.000 with the plain prompt, and with the
rules prompt too. A test that everything passes cannot tell prompts or models apart, so two harder files were
added, built from near-misses that differ in one decisive attribute (`304` vs `304L`, raised face vs flat face,
Viton vs EPDM seal, copper vs aluminium cable, 2-pole vs 4-pole motor) and from duplicates that look different
(`SPANNER` vs `WRENCH`, `2 IN` vs `DN50`, `3PH` vs `3 PHASE`, `J/CRANE` vs `JOHN CRANE`).

| Dataset | Pairs | Rules baseline: accuracy | F1 | False alarms | Missed duplicates |
|---|---|---|---|---|---|
| `pairs.csv` (easy) | 60 | 0.883 | 0.881 | 3 | 4 |
| `pairs_hard.csv` (dev) | 24 | 0.500 | 0.455 | 5 | 7 |
| `pairs_heldout.csv` (held-out) | 12 | 0.583 | 0.615 | 3 | 2 |

The baseline drops from 88% to 50% on the hard set, so this set separates matchers. Reports:
[`reports/rules-hard/report.md`](reports/rules-hard/report.md),
[`reports/rules-heldout/report.md`](reports/rules-heldout/report.md).

**How to use the three files.** `pairs.csv` is a sanity check. `pairs_hard.csv` is the set to tune prompts and
rules on. `pairs_heldout.csv` must not be used for tuning: run it once at the end, on the final prompt and model,
and report that number. Only 12 pairs, so one wrong answer moves the score by 8 points.

### LLM results

Recorded so far (Groq, `openai/gpt-oss-120b`, easy set, 60 pairs): prompt v1 accuracy 1.000, prompt v2 accuracy 1.000.
Results on the hard and held-out sets are not recorded here yet. To add them, run the commands in
[Evaluating an LLM](#evaluating-an-llm) with `--data data/pairs_hard.csv` and add the table here.

## Labelling guideline

Two descriptions are labelled **duplicate** when they describe the same item: type, size, rating,
material, grade, voltage, length, manufacturer and part number all match. The following are **not**
differences: word order, case, punctuation, abbreviations (SS = stainless steel), and the same value in
another notation (`1/2"` = `1/2 INCH`, `2 IN` = `50 MM`, `150#` = `CLASS 150`).

Items from different manufacturers are labelled **different** even when interchangeable on paper
(`6205-2RS SKF` vs `6205-2RS FAG`), because they carry different manufacturer part numbers.
Each row in the data files has a `category` and a `note` explaining the label.

**The labels were written by one person and have not been reviewed by a domain expert.** Several hard cases depend on engineering conventions (for example, `2 IN` = `DN50`, `gG` vs `aM` fuses). A materials or maintenance engineer should check them before the scores are used for any real decision.

## Project structure

```
data/pairs.csv           60 easy labelled pairs: id, a, b, label, category, note
data/pairs_hard.csv      24 near-miss and hard-duplicate pairs (for tuning)
data/pairs_heldout.csv   12 hard pairs, not for tuning
dedupe/normalize.py      text normalisation for the baseline
dedupe/matchers.py       RulesMatcher, LLMMatcher, prompts v1 and v2, answer parsing, cache
dedupe/metrics.py        confusion matrix, precision / recall / F1, per-category accuracy
dedupe/run.py            run one matcher, write results.csv, summary.json, report.md
dedupe/compare.py        side-by-side table of finished runs
tests/                   dataset checks, metric tests, baseline regression gate, LLM plumbing tests
reports/rules/           baseline report generated by this repo
.github/workflows/       CI
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                                                # all tests, no API key needed
python -m dedupe.run --matcher rules --out reports/rules
```

## Evaluating an LLM

```bash
export ANTHROPIC_API_KEY=...        # Windows PowerShell: $env:ANTHROPIC_API_KEY="..."
export LLM_MODEL=<model name>       # a model your account can use

python -m dedupe.run --matcher llm --prompt v1 --data data/pairs_hard.csv --out reports/hard-llm-v1
python -m dedupe.run --matcher llm --prompt v2 --data data/pairs_hard.csv --out reports/hard-llm-v2
python -m dedupe.compare reports/rules-hard reports/hard-llm-v1 reports/hard-llm-v2
```

- `--workers N` sends N calls at once (default 4 for an LLM, 1 for the rules matcher). Results and their order are identical to a sequential run; this only makes it faster.
- `--provider groq` uses Groq's OpenAI-compatible endpoint with `GROQ_API_KEY`; set `LLM_MODEL` to a model listed in your Groq console.
- Prompt `v1` asks the question plainly. Prompt `v2` states the matching rules (which differences matter and which do not). Comparing them shows how much of the result comes from the prompt.
- Every answer is cached in `.cache/llm_answers.jsonl`, keyed by provider, model, prompt version and texts. Re-running is free and reproducible, and changing the model or prompt triggers new calls only for what changed.
- If answers are unusable, the report starts with a warning (those pairs are scored as "not duplicate", which makes accuracy misleading), the console prints the first error with the provider's own message, and the run exits with an error when every answer failed.
- An answer that is not valid JSON, or has no boolean `duplicate`, is counted as `unusable` and reported separately; it is never guessed.
- Rate limits (HTTP 429) and server errors (5xx) are retried up to 5 times, honouring the `retry-after` header. If a call still fails, that pair is reported as `unusable` with the error, the failure is not cached, and the run continues. Re-running fills in only the missing pairs, which makes the free tiers of the providers practical to use.
- To use another provider, pass your own `call_fn(prompt, model) -> str` to `LLMMatcher`.

### Troubleshooting an LLM run

| Symptom | Likely cause |
|---|---|
| Every pair says `API error ... 404 ... model_not_found` | wrong or unavailable model name in `LLM_MODEL`; check the provider's model list |
| `401` | wrong or missing API key |
| `429` after retries | rate limit; wait and re-run, only the missing pairs are called again |
| High `unusable` count without API errors | the model's reply was not JSON; open `results.csv` and read the `reason` column |

## Tests

| File | Checks |
|---|---|
| `test_dataset.py` | for all three files: unique ids, binary labels, class balance, no empty or repeated pairs (also across files), id suffix matches label, hard sets are not copies of the easy set |
| `test_metrics.py` | confusion counts, hand-calculated precision / recall / F1 (asymmetric so the two cannot be swapped), zero-division cases |
| `test_normalize.py` | abbreviations, number-unit splitting, case and whitespace |
| `test_baseline.py` | F1 regression gate (0.85), zero false alarms on size / rating / part-number / material differences, spot checks, one expected failure for unit conversion |
| `test_llm_matcher.py` | JSON parsing (clean, fenced, malformed), prompt content, cache hits and cache separation per model and prompt, unusable answers counted, a fake model that agrees with everything scores precision 0.5, API errors reported and not cached, retry on 429 / 5xx, no retry on client errors, a parallel run gives identical answers and an uncorrupted cache |

**The tests were checked by breaking the code on purpose.** Disabling the numeric check, swapping the
precision or recall formula, and letting the parser accept a string as a boolean each made tests fail.
One such check showed a metric test was too weak (equal false positives and false negatives hide a swapped
formula), and it was rewritten with an asymmetric example.

## Design decisions

- **One interface for every matcher.** Anything with `predict(a, b)` can be scored, which keeps the comparison fair.
- **Report both error types.** A false alarm merges two different parts; a missed duplicate leaves clutter. They are not equally costly.
- **Per-category accuracy.** A good overall score can hide a category that always fails.
- **Cached, injectable model calls.** Results are reproducible, tests need no network, and cost stays low.
- **A named regression gate.** The baseline's F1 is pinned in CI so rule changes cannot quietly make it worse.

## Limitations

- **Small and synthetic.** 96 pairs, written by one person in the style of MRO descriptions. They are not customer data, and results on real catalogues will differ. On the 60-pair set, one wrong answer moves accuracy by about 1.7 points, so small differences between runs are not meaningful.
- **The baseline is optimistic.** Its abbreviation list was written knowing the dataset, so its score on unseen descriptions would likely be lower. A held-out set labelled by someone else would test this.
- **LLM output varies.** Models change and answers can differ between runs; the cache fixes results for a given model and prompt but does not make the model deterministic.
- **The LLM matcher was tested with a fake model only.** The HTTP calls to Anthropic and Groq follow the providers' documented request formats but have not been run against the live services in this repository's test environment.
- **Pair-level task only.** It does not yet cover finding duplicates across a whole catalogue, part classification, or stock-level recommendations.

## Roadmap

- A larger held-out set labelled by a second person, and confidence intervals on the scores.
- A parts-classification task (assign a category to each description) using the same harness.
- Track scores per release in a CSV so accuracy over time can be charted.
- Larger pairs set including near-miss part numbers generated from real standards.
