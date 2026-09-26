# Selective verification of agent memory

Status: proposed research extension. No selective-verification results are included in this release.

## Research question

Can an agent decide when to verify a remembered procedure without being explicitly told that the policy changed, reducing errors relative to unchecked reuse and cost relative to checking every task?

## Business purpose

The intended benefit is less repeated investigation and fewer mistakes caused by obsolete procedures. Measure total cost per successfully completed task, including failed attempts, verification, retries and human review. Staff time released is a capacity benefit; it is cash savings only if spending is actually avoided. Current utility scores are synthetic points, not financial ROI.

## Proposed implementation

1. Add tasks with natural-language runbooks and multiple actions rather than a binary maintenance choice.
2. Introduce policy changes with clear, weak and absent observable signals. Include harmless changes that should not invalidate a lesson.
3. Record candidate signals: time since verification, changed dependencies, document fingerprints, conflicting memories and prior task failures. Include the impact of an incorrect action.
4. Add a selector that chooses reuse, verification or deferral before taking action. Keep the hidden policy schedule and evaluator truth inaccessible to it.
5. Implement verification tools such as policy lookups, dry runs and precondition tests. Some checks should fail or return ambiguous evidence.
6. Record the full cost of every path, including checks and unresolved tasks.

An initial decision rule would verify when the estimated reduction in expected failure loss exceeds verification cost. Calibration must use validation data; model confidence alone is not a calibrated error probability. When no pre-action signal distinguishes a changed world, targeted detection cannot be assumed. Periodic checks remain a necessary comparator.

## Baselines

- Always verify.
- Reuse matching memory without additional verification.
- Periodic and random verification, with comparable checking budgets.
- Current-document retrieval and exact scope filtering.
- Official ACE, compared with otherwise identical ACE plus selective verification.

The current recency and frequency policies are simplified baselines, not implementations of published agent-memory systems.

## Evaluation

Use separate training, validation and held-out test task families. Set thresholds on validation data. Score each action before allowing its result to update memory. Compare policies on matched task streams with fixed model and tool configurations.

Measure consequential errors per attempted task, completion rate, elapsed time, total cost per success, stale-memory errors before detection, recovery time and unnecessary checks. Report deferrals and abandoned tasks separately. Compare multiple verification budgets and paired uncertainty intervals across independent streams.

Success requires fewer errors than unchecked reuse, lower cost than always checking at a predefined acceptable error tolerance, and improvement over simple budget-matched checking schedules. Report negative findings if the selector adds no value or only looks safer because it defers difficult work.

## Milestones

- [x] Six-policy deterministic simulator and reproducible pilot.
- [x] SQLite audit records and individual decision traces.
- [x] Optional Ollama adapter with mocked contract tests.
- [ ] End-to-end real-model evaluation.
- [ ] Selective-verification policy and imperfect checks.
- [ ] Periodic and random-check baselines.
- [ ] Stronger task families and held-out evaluation.
- [ ] Independent replication and research review.

Before a novelty claim, review related work on selective prediction, change detection and risk-based verification. No claim of being the first method or outperforming ACE is made here.
