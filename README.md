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
