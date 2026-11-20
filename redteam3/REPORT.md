# Red team 3 report: L-03-003
Independent re-implementation from plan text and raw data. Code in this folder (ccm3.py, run.py, look.py, decomp.py, fair.py, kordist.py, strat.py, nopron.py; exploratory: tadmor.py, nelx.py).

## Replication
Inheritance pooled I +0.676 (CI 0.37 to 0.98), 13/13. jpn ratio 2.07 p=0.0036 I=+0.200; kor ratio 2.88 p=0.0001 I=+0.364. Kho-Bwa pooled I +0.213 (CI -0.17 to 0.63). Identical to builder.
Fragility: without the prefix rule, jpn overall p=0.0112 (borrowing side would be UNTESTED) and Kho-Bwa I CI lower bound +0.003.

## Diagnosis (corrects the builder)
- Japanese: signal is loans (today, six, three, meat, two, liver, sun); removing 7 loan concepts gives ratio 0.84. Loans sit on Holman items because Holman measures inheritance stability, not borrowing resistance, and NorthEuraLex lists Sino-Japanese numerals first.
- Korean: about 70% of stable-tier excess is NOT loans (pronouns na/nʌ vs ŋa/ni, chance matches). 
- KEY FINDING: Korean vs the 12 DISTANT Sino-Tibetan languages (no Chinese involved): ratio 2.37, p=0.0001; with a word-shape-stratified null still 2.07, p=0.0002. An unrelated language passes the group test used for Kho-Bwa. The 14 calibration negatives (all non-East-Asian) max out at 1.70. The method has a false-positive floor near 2 for typologically East Asian languages (CV syllables, nasal pronouns, n/ŋ merged in class N, vowel-initial words coded H).
- Ratio comparison jpn/kor-vs-Sinitic to Kho-Bwa-vs-DISTANT is confounded (6 near-duplicate Sinitic references).

## Verdicts
(a) Calibration failure real 95%; builder diagnosis right for jpn 75%, wrong for kor 80%.
(b) Downgrade of L-03-002 framing justified 85%, decisively because Korean vs DISTANT sits inside Kho-Bwa's range (1.88 to 2.83).
(c) Next test: calibration inside NorthEuraLex with known loan pairs vs inherited pairs, Leipzig-Jakarta tier, shape-stratified null, empirical null for I from Korean and negatives. Exploratory: loan pairs I -0.099 to +0.002; inherited +0.004 to +0.206. Borrowing signature is I near 0, not negative.
