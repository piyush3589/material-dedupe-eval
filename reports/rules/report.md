# Evaluation report: rules

Pairs: 60  |  unusable answers: 0

| Metric | Value |
|---|---|
| Accuracy | 0.883 |
| Precision | 0.897 |
| Recall | 0.867 |
| F1 | 0.881 |

| | Predicted duplicate | Predicted not duplicate |
|---|---|---|
| **Actually duplicate** | 26 | 4 |
| **Actually different** | 3 | 27 |

## Accuracy by category

| Category | Correct | Total |
|---|---|---|
| abbreviation | 10 | 10 |
| different_manufacturer | 1 | 1 |
| different_material | 3 | 3 |
| different_part_number | 4 | 4 |
| different_rating | 7 | 7 |
| different_size | 10 | 10 |
| different_type | 2 | 5 |
| formatting | 1 | 1 |
| part_number_format | 2 | 4 |
| unit_conversion | 0 | 1 |
| unit_notation | 1 | 2 |
| word_order | 12 | 12 |

## Wrong answers (7)

| ID | Type | Expected | A | B | Why the matcher said so |
|---|---|---|---|---|---|
| P10 | missed duplicate | duplicate | V-BELT B68 | VBELT B-68 | word overlap 0.50 < 0.6 |
| P15 | missed duplicate | duplicate | OIL FILTER CAT 1R-0750 | CATERPILLAR OIL FILTER 1R0750 | word overlap 0.50 < 0.6 |
| P17 | missed duplicate | duplicate | BOLT HEX 1/2-13 UNC X 2 IN GR8 | HEX BOLT 1/2 13 UNC 2IN GRADE 8 | numeric attributes differ: ['GR8'] |
| P19 | missed duplicate | duplicate | VALVE BALL 2IN SS316 FLANGED 150# | BALL VALVE 50MM STAINLESS STEEL 316 FLG CLASS 150 | numeric attributes differ: ['2'] |
| N05 | false alarm | different | VALVE GATE 2IN 150# CS FLANGED | VALVE GLOBE 2IN 150# CS FLANGED | numbers agree, word overlap 0.75 |
| N27 | false alarm | different | STRAINER Y TYPE 3IN 150# CS | STRAINER BASKET TYPE 3IN 150# CS | numbers agree, word overlap 0.75 |
| N29 | false alarm | different | WASHER FLAT M10 SS | WASHER SPRING M10 SS | numbers agree, word overlap 0.60 |
