# Duplicate Material Detection: Evaluation Suite

A tool that checks how well a system can tell whether two spare-part descriptions
are the same item.

## The problem

The same part is often written in different ways, for example:

- `BEARING, BALL, 6205-2RS, SKF`
- `SKF BALL BEARING 6205 2RS`

But two similar names can also be different parts, like a 6205 and a 6305 bearing.
Merging two different parts by mistake costs more than missing a duplicate. So this
tool counts the two kinds of mistakes separately.

## What it does

- Takes pairs of part descriptions, each labelled "same" or "different".
- Runs any matcher on them (a rules-based one, or an LLM).
- Scores it with accuracy, precision, recall and F1, and lists the wrong answers.

## The data

96 labelled pairs in three files:

| File | Pairs | Use |
|---|---|---|
| `pairs.csv` | 60 easy | Sanity check |
| `pairs_hard.csv` | 24 hard | Tune the prompt and rules |
| `pairs_heldout.csv` | 12 hard | Run once at the end, never for tuning |

## Results so far

The rules-based baseline scored:

### How the accuracy numbers add up

| Dataset | Pairs | Wrong (false alarms + missed) | Correct | Accuracy |
|---|---|---|---|---|
| Easy | 60 | 3 + 4 = 7 | 53 | 0.883 |
| Hard | 24 | 5 + 7 = 12 | 12 | 0.500 |
| Held-out | 12 | 3 + 2 = 5 | 7 | 0.583 |

These numbers are for the rules baseline only.
### Hard set results (24 pairs)

| Matcher | Accuracy | F1 | False alarms | Missed duplicates |
|---|---|---|---|---|
| Rules baseline | 0.500 | 0.455 | 5 | 7 |
| LLM, prompt v1 (`gpt-oss-120b`) | 1.000 | 1.000 | 0 | 0 |
| LLM, prompt v2 (`gpt-oss-120b`) | 0.958 | 0.957 | 0 | 1 |

For the LLM runs, precision was 1.000 for both prompts. Recall was 1.000 for v1 and 0.917 for v2.
v2 missed one pair (HP02: `BEARING` vs `BERING`).

An LLM scored 1.000 on the easy set with both prompts. A test that everything passes
cannot tell systems apart, so I added the hard set. On it, the baseline falls from
0.883 to 0.500.

LLM results on the hard and held-out sets are not recorded yet.

### What the rules baseline does

| Step | What it does | Example |
|---|---|---|
| Clean the text | Ignore case and punctuation, expand abbreviations, split `10mm` into `10 mm` | `6205-2RS` and `6205 2RS` look the same |
| Match numbers | Every number in one description must appear in the other | `6205` vs `6305` is a different part |
| Check word overlap | Remaining words must overlap above a threshold | Gate valve vs globe valve still overlaps too much, so it gives a false alarm |

## Where the baseline fails

- `2 IN` and `50 MM` are not treated as the same size.
- `CAT` is not recognised as Caterpillar.
- Gate valve vs globe valve looks similar to it, because the type is only one word.

### The two prompts

| | v1 | v2 |
|---|---|---|
| Idea | Ask plainly | State the matching rules |
| Rules given | None | Every attribute must match; word order, abbreviations, punctuation, case and unit notation do not count as differences |
| When unsure | Not stated | Answer false |

**v1:** "Are these two spare-part descriptions the same item?" The model replies with JSON only:
`{"duplicate": true or false, "reason": "short reason"}`.

**v2** tells the model that every technical attribute (type, size, pressure rating, material,
grade, voltage, length, part number, manufacturer) must match, lists which differences do not
matter, and says: "If an attribute differs or you are unsure, answer false."

**Why v2 lowered recall:** the typo pair `BEARING` vs `BERING` (HP02) is not on v2's list of
allowed differences, so v2 answered false for a pair labelled as a duplicate. Precision stayed at
1.000. This is one pair, so it shows how the prompt can change results but does not prove it.

## How I checked the tests

I broke the code on purpose (for example, swapping the precision and recall formulas)
and confirmed that tests failed. One test was too weak, so I rewrote it.

## Quick start

```bash
pip install -r requirements.txt
pytest
python -m dedupe.run --matcher rules --out reports/rules
```

## Limitations

- Small and made up by one person. 96 pairs, not customer data.
- No domain expert has reviewed the labels.
- The baseline's abbreviation list was written knowing the data, so its score is optimistic.
- The repository's tests use a fake model. 
## Roadmap

- A bigger held-out set labelled by a second person.
- A parts-classification task using the same tool.
- Track scores per release.
