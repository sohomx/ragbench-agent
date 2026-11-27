# runs

recorded traces and result json live here, one file per run. they are committed on purpose: every number in the README results table links to a file in this folder.

- one file per run, named so it sorts by date, e.g. `2026-12-07-bm25-baseline.json`.
- written by the eval runner or the agent harness, never edited by hand. if a number is wrong, fix the code and make a new run.
- `latest-stub.json` is the output of the eval stub (`python -m evals.run_eval`) and is gitignored.
