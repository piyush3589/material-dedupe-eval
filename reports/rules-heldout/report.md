# Evaluation report: rules

Pairs: 12  |  unusable answers: 0

| Metric | Value |
|---|---|
| Accuracy | 0.583 |
| Precision | 0.571 |
| Recall | 0.667 |
| F1 | 0.615 |

| | Predicted duplicate | Predicted not duplicate |
|---|---|---|
| **Actually duplicate** | 4 | 2 |
| **Actually different** | 3 | 3 |

## Accuracy by category

| Category | Correct | Total |
|---|---|---|
| abbreviation | 1 | 2 |
| different_material | 1 | 1 |
| different_part_number | 1 | 1 |
| different_rating | 0 | 1 |
| different_size | 1 | 1 |
| different_type | 0 | 2 |
| part_number_format | 1 | 1 |
| synonym | 0 | 1 |
| unit_notation | 2 | 2 |

## Wrong answers (5)

| ID | Type | Expected | A | B | Why the matcher said so |
|---|---|---|---|---|---|
| XN02 | false alarm | different | CONTACTOR 3P 25A 24VDC | CONTACTOR 3P 25A 24VAC | numbers agree, word overlap 0.60 |
| XN04 | false alarm | different | ELBOW 90DEG LR 3IN SCH40 CS BW | ELBOW 90DEG SR 3IN SCH40 CS BW | numbers agree, word overlap 0.78 |
| XN06 | false alarm | different | TRANSMITTER PRESSURE 0-10 BAR 4-20MA HART | TRANSMITTER PRESSURE 0-10 BAR 4-20MA | numbers agree, word overlap 0.80 |
| XP02 | missed duplicate | duplicate | CONTACTOR 3P 25A 24VDC | CONTACTOR 3 POLE 25 AMP 24 V DC | word overlap 0.29 < 0.6 |
| XP04 | missed duplicate | duplicate | GREASE LITHIUM EP2 18KG PAIL | GREASE LI EP-2 18 KG BUCKET | word overlap 0.29 < 0.6 |
