# Evidence and claim boundaries

Review date: 2026-09-15. This is a focused narrative review, not exhaustive literature screening.

| Claim group | Supporting material | Scope |
|---|---|---|
| Original ACE architecture and benchmark row | Reference 1, sections 3–4 and Table 1 | Published authors' evidence; not reproduced here |
| Reflection and memory mechanisms | References 2–7 | Used to position the research question; scores are not pooled |
| Context utilization concern | Reference 8 | Historical model experiments; no automatic extrapolation to current models |
| Memory injection risk | Reference 9 | Motivates the threat model; pilot does not implement this attack |
| More realistic execution benchmark | Reference 10 | Future evaluation option; not run |
| Official upstream code | Reference 11 | Independent implementation; no code copied |
| Local inference API | Reference 12 | Adapter protocol reference; no model execution performed |
| Pilot means and intervals | results/pilot/summary.json and paired.json | Executed deterministic simulation |
| Reproduction inputs | results/pilot/manifest.json and traces.jsonl | Seeded synthetic streams with full traces |

Novelty claim: a small operational evaluation artifact and applicability-focused design argument. No claim of inventing context adaptation, provenance, metadata filtering or reflective memory. A stronger novelty claim requires a broader literature search and real-model evidence.

## Publication gate

- Confirm author names, affiliations and AI-assistance disclosure.
- Run real models on held-out task families and preserve model digests.
- Compare official ACE and current-document retrieval under matched budgets.
- Add unreliable inspection, unmarked corruption and delayed feedback.
- Measure tokens, latency and human effort rather than using utility as dollars.
- Obtain an independent review of methods, statistical analysis and conclusions.
- Publish the repository/release, then add its exact URL and archival identifier.

## Privacy

All task data are synthetic. No Oracle, Visa, customer, Jira, GitHub-account or production environment records are used. No research publication or remote repository creation has occurred.
