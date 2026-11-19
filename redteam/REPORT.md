# Red team report: CAL-001 and L-03-001
Independent re-implementation from the sealed plan text only (no access to bench/, runs/, ledger/).
Code: redteam/run.py, explore.py, randdrop_kb.py. Tables: out_0.md (as-specified), out_1..7.md, explore_out.txt, randdrop_kb.txt.

## Replication (plan as written)
- CAL-001 PASS: 12/13 positives (Bantawa missed, p=0.084), 0/14 negatives.
- L-03-001 primary: 2/22 Holm<0.01 (Duhumbi, Khispi). Builder found 3/22 (also Khoina); difference is RNG-level.
- L-03-001 purged: 0/22. Puroik Li 0.124/0.332, Sun 0.038/0.174 (primary/purged raw p).
- Rawa is also a Puroik doculect (Glottolog); the plan's Puroik list omitted it. Rawa: 0.106/0.327.

## Decisive attack (exploratory): the purge has no power
Applying the identical purge to CAL-001 positives: 4/13 pass (31%), so calibration FAILS for the purged test.
Random removal of the same number of concepts leaves positives at 11/13, so the loss comes from WHICH concepts the purge removes:
contact languages are themselves Sino-Tibetan, so inherited roots (2sg 63/64 removed, fish 36/40, tongue 26/30) get purged as "contact".
Purge removes 38% of Kho-Bwa's matches with DISTANT.

## Second attack (exploratory): prefix coding hides roots
41% of Kho-Bwa codes start with H (vs 11% in DISTANT) because prefixes (a-, ə-, mə-, aŋ33-) become the first consonant.
Prefix-aware coding (strip leading V/CV before a morpheme boundary, all datasets):
CAL-001 13/13 pass, 0/14 false positives; L-03 primary 9/22; purged 2/22; Kho-Bwa vs 14 unrelated languages: 0/22 false positives.
Puroik primary raw p: Sun 0.0019, Li 0.0139, Rawa 0.0094 (none survives Holm).

## Verdict
Numbers replicate; interpretation falls. The purged test is UNINTERPRETABLE (about 30% power on known relatives).
Puroik is the weakest-matching part of Kho-Bwa under every variant: a real relative finding, not evidence of isolate status.
Confidence: about 90% that the purge-power failure is robust; about 65% that the prefix-aware coding is the right one.
Limitation: the red team is the same model family as the builder.
