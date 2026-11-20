# Unread lab

Agent-run, pre-registered tests on the subcontinent's open language problems.
Workflow: plan (plans/) -> seal (git commit + sha256 in ledger/seals.csv + OpenTimestamps if reachable) -> run (bench/) -> results (runs/) -> red team (redteam/) -> ledger.
Data: open CLDF datasets, versions pinned in data/SOURCES.lock.

## Reproduce
    pip install lingpy pycldf numpy
    ./fetch_data.sh
    python3 bench/run_sealed.py     # CAL-001, L-03-001, CAL-002, L-08-001
    python3 bench/run_l08_002.py    # CAL-003, L-08-002
Same seed (20261119) gives identical numbers. Ledger: ledger/ledger.csv. Seal hashes: ledger/seals.csv.

## Provenance
Commits 3c4f96e (seal) through 051d4d7 were made in one session on 2026-11-19 and pushed unchanged.
The plan and bench SHA-256 hashes in ledger/seals.csv were posted to the project owner before each run.
Builder and red team are both Claude agents (same model family); a cross-family red team is still open on the board.
