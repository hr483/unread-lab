# Red team 2 report: L-03-002
Independent re-implementation from plans/L-03-002.yaml and the base method text. No access to bench/, runs/, ledger/, redteam/.
Code: core.py, run_main.py, attack_*.py; outputs out_*.txt.

## Replication: headline numbers reproduce exactly
- CAL-004 PASS 13/13, 0/14 FP. Sulong ratio 1.70, p=0.0151 (fails 0.01), rank 14/14. Idu, Kaman, Bokar pass; Darang fails (1.46).
- CAL-005 PASS 13/13, 0/14 FP. TEST_B 8/8 Holm p=0.0008, ratios 2.05-2.87 (positives 1.92-3.63).

## Corrections to the plan (builder error)
- TEST_A data is NOT independent. suntb Sulong is the same Sun 1991 recording as khobwa Eastern_Puroik_Sun used in L-03-001:
  63 of 84 shared concepts have identical first forms; 57 of the 77 TEST_A concepts were already in L-03-001's 76.
- DISTANT_SUN is all Lolo-Burmese and 10/13 positives are Qiangic/rGyalrongic: a narrow reference.

## Attacks (exploratory)
- Contact filter (drop Kho-Bwa forms matching Tibetan/Tshangla where that form is not shared with DISTANT): Kho-Bwa 8/8 at every threshold tried; calibrated version (spare if >=2 DISTANT match) keeps positives 13/13 and Kho-Bwa 8/8.
- Borrowing-prone classes removed (nursery, numerals, culture items): Kho-Bwa 8/8 while calibration holds.
- Strict prefix inventory: TEST_B 8/8; Sulong p=0.018, still rank 14.
- Fragility: top 10 concepts carry 48% of matches (STONE/HEART luŋ, FATHER, MOTHER); removing each language's top 5 leaves Kho-Bwa 2/8 and positives 3/13. Equally fragile.
- 8 doculects form about 3 independent clusters.
- Puroik vs a diverse ST reference (seen data): Sun recording ratio 1.94, above the weakest positive (Batang 1.81).

## Verdict
- Western Kho-Bwa resembles distant ST as strongly as known members: SURVIVES (about 85%). About 70% that it is not mainly Tibetan/Tshangla loans. Contact with untested neighbours not excluded.
- Puroik below the sealed threshold: SURVIVES (about 90%; p 0.015-0.060 across all codings).
- Puroik as the weakest / less ST than accepted members: DOES NOT SURVIVE as an interpretation (about 35%).
