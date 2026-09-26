# Pilot evidence

These are deterministic simulation outputs, not production data or LLM evaluations. The original run used 20 seeds, 240 tasks, six methods and five scenarios: 144,000 decision records.

## Read the results

- [summary.json](summary.json): post-midpoint means and uncertainty intervals.
- [paired.json](paired.json): paired comparisons.
- [per_seed.csv](per_seed.csv): all/pre/post aggregates.
- [manifest.json](manifest.json): configuration and source hashes.
- [playbooks.json](playbooks.json): seed-0 memories.
- [comparison.png](comparison.png): results chart.
- [report.html](report.html): standalone report; download it and open it locally.

## Inspect compressed evidence

The full original trace is stored losslessly as `traces.jsonl.gz`. Seed-0 SQLite files are stored in `sqlite-audit.zip`. From this directory:

```bash
python -c "import gzip, shutil; shutil.copyfileobj(gzip.open('traces.jsonl.gz', 'rb'), open('traces.jsonl', 'wb'))"
python -m zipfile -e sqlite-audit.zip audit
```

Each SQLite database contains `bullets` and `events` tables. New CLI runs produce uncompressed traces and databases directly. Checksums are in `SHA256SUMS`.

The trust flag is supplied by the simulator. Zero errors with the gate do not show autonomous detection of bad feedback. Selective verification has not been implemented or evaluated.
