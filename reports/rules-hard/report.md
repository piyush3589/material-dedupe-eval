# Evaluation report: rules

Pairs: 24  |  unusable answers: 0

| Metric | Value |
|---|---|
| Accuracy | 0.500 |
| Precision | 0.500 |
| Recall | 0.417 |
| F1 | 0.455 |

| | Predicted duplicate | Predicted not duplicate |
|---|---|---|
| **Actually duplicate** | 5 | 7 |
| **Actually different** | 5 | 7 |

## Accuracy by category

| Category | Correct | Total |
|---|---|---|
| abbreviation | 1 | 3 |
| different_face_type | 0 | 1 |
| different_material | 1 | 3 |
| different_part_number | 1 | 1 |
| different_rating | 2 | 2 |
| different_seal_type | 1 | 1 |
| different_thread_pitch | 1 | 1 |
| different_type | 1 | 3 |
| formatting | 1 | 1 |
| synonym | 2 | 2 |
| typo | 0 | 1 |
| unit_conversion | 0 | 2 |
| unit_notation | 0 | 2 |
| word_order | 1 | 1 |

## Wrong answers (12)

| ID | Type | Expected | A | B | Why the matcher said so |
|---|---|---|---|---|---|
| HN04 | false alarm | different | FLANGE WN 4IN 150# RF CS | FLANGE WN 4IN 150# FF CS | numbers agree, word overlap 0.78 |
| HN06 | false alarm | different | FUSE CARTRIDGE 10A 250V GG | FUSE CARTRIDGE 10A 250V AM | numbers agree, word overlap 0.67 |
| HN09 | false alarm | different | VALVE BALL 2IN 150# SS316 FLANGED FULL BORE | VALVE BALL 2IN 150# SS316 FLANGED REDUCED BORE | numbers agree, word overlap 0.80 |
| HN10 | false alarm | different | PUMP SEAL MECHANICAL 40MM JOHN CRANE 2100 VITON | PUMP SEAL MECHANICAL 40MM JOHN CRANE 2100 EPDM | numbers agree, word overlap 0.75 |
| HN11 | false alarm | different | CABLE POWER 3CORE 2.5MM2 CU PVC 1.1KV | CABLE POWER 3CORE 2.5MM2 AL PVC 1.1KV | numbers agree, word overlap 0.67 |
| HP02 | missed duplicate | duplicate | BEARING BALL 6205-2RS SKF | BERING BALL 6205 2RS SKF | word overlap 0.50 < 0.6 |
| HP03 | missed duplicate | duplicate | PIPE SS 304 SCH40 2IN 6M | PIPE STAINLESS STEEL AISI 304 SCH 40 50 MM NB 6 METER | numeric attributes differ: ['2', '50'] |
| HP05 | missed duplicate | duplicate | MOTOR ELECTRIC 3PH 5.5KW 4P 415V | ELECTRIC MOTOR 3 PHASE 5.5 KW 4 POLE 415 VOLT | word overlap 0.43 < 0.6 |
| HP08 | missed duplicate | duplicate | VALVE BALL 2IN 150# SS316 FLANGED FULL BORE | BALL VALVE DN50 CLASS 150 SS316 FLANGED FULL BORE | numeric attributes differ: ['2', 'DN50'] |
| HP09 | missed duplicate | duplicate | CABLE POWER 3CORE 2.5MM2 CU PVC 1.1KV | CABLE POWER 3 X 2.5 SQMM COPPER PVC 1100V | numeric attributes differ: ['1100', '11KV', 'MM2'] |
| HP10 | missed duplicate | duplicate | FUSE CARTRIDGE 10A 250V GG | CARTRIDGE FUSE 10 AMP 250 VOLT gG | word overlap 0.43 < 0.6 |
| HP12 | missed duplicate | duplicate | PUMP SEAL MECHANICAL 40MM JOHN CRANE 2100 VITON | MECH SEAL 40MM J/CRANE 2100 VITON | word overlap 0.33 < 0.6 |
