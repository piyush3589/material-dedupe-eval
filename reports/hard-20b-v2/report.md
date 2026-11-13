# Evaluation report: llm-groq-openai/gpt-oss-20b-v2

Pairs: 24  |  unusable answers: 0

| Metric | Value |
|---|---|
| Accuracy | 0.833 |
| Precision | 1.000 |
| Recall | 0.667 |
| F1 | 0.800 |

| | Predicted duplicate | Predicted not duplicate |
|---|---|---|
| **Actually duplicate** | 8 | 4 |
| **Actually different** | 0 | 12 |

## Accuracy by category

| Category | Correct | Total |
|---|---|---|
| abbreviation | 3 | 3 |
| different_face_type | 1 | 1 |
| different_material | 3 | 3 |
| different_part_number | 1 | 1 |
| different_rating | 2 | 2 |
| different_seal_type | 1 | 1 |
| different_thread_pitch | 1 | 1 |
| different_type | 3 | 3 |
| formatting | 1 | 1 |
| synonym | 0 | 2 |
| typo | 0 | 1 |
| unit_conversion | 1 | 2 |
| unit_notation | 2 | 2 |
| word_order | 1 | 1 |

## Wrong answers (4)

| ID | Type | Expected | A | B | Why the matcher said so |
|---|---|---|---|---|---|
| HP01 | missed duplicate | duplicate | WRENCH SPANNER COMBINATION 17MM | SPANNER COMBINATION 17 MM | type differs (wrench vs spanner) |
| HP02 | missed duplicate | duplicate | BEARING BALL 6205-2RS SKF | BERING BALL 6205 2RS SKF | Spelling mismatch in type |
| HP03 | missed duplicate | duplicate | PIPE SS 304 SCH40 2IN 6M | PIPE STAINLESS STEEL AISI 304 SCH 40 50 MM NB 6 METER | NB attribute present in B but missing in A |
| HP11 | missed duplicate | duplicate | WASHER FLAT M10 SS316 | WASHER PLAIN M10 STAINLESS STEEL 316 | type mismatch (FLAT vs PLAIN) |
