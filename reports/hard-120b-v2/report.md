# Evaluation report: llm-groq-openai/gpt-oss-120b-v2

Pairs: 24  |  unusable answers: 0

| Metric | Value |
|---|---|
| Accuracy | 0.958 |
| Precision | 1.000 |
| Recall | 0.917 |
| F1 | 0.957 |

| | Predicted duplicate | Predicted not duplicate |
|---|---|---|
| **Actually duplicate** | 11 | 1 |
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
| synonym | 2 | 2 |
| typo | 0 | 1 |
| unit_conversion | 2 | 2 |
| unit_notation | 2 | 2 |
| word_order | 1 | 1 |

## Wrong answers (1)

| ID | Type | Expected | A | B | Why the matcher said so |
|---|---|---|---|---|---|
| HP02 | missed duplicate | duplicate | BEARING BALL 6205-2RS SKF | BERING BALL 6205 2RS SKF | Spelling difference ('BEARING' vs 'BERING') is not an allowed variation, so cannot confirm they describe the same item |
