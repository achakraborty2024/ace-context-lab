# ACE Context Lab

**Can an agent reuse experience without repeating yesterday's obsolete rule?**

[![Tests](https://github.com/achakraborty2024/ace-context-lab/actions/workflows/tests.yml/badge.svg)](https://github.com/achakraborty2024/ace-context-lab/actions/workflows/tests.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Research pilot](https://img.shields.io/badge/Status-research%20pilot-orange)

A reproducible Python + SQLite lab for **agent memory, policy drift, context engineering, and operational efficiency**.

[Quick start](#run-in-two-minutes) · [Results](#pilot-results) · [Research paper](paper/research-paper.md) · [Selective-verification roadmap](docs/selective-verification.md) · [Contributing](CONTRIBUTING.md)

## Contents

- [Why this matters](#why-this-matters)
- [Business value and ROI](#business-value-and-roi)
- [Run in two minutes](#run-in-two-minutes)
- [Pilot results](#pilot-results)
- [How the simulation works](#what-happens)
- [Scenarios](#scenarios)
- [Optional language-model experiment](#optional-real-language-model-experiment)
- [Outputs and audit](#outputs-and-audit)
- [Research boundaries](#research-boundaries)

## Why this matters

An operational agent can repeat a once-successful procedure after the rules change. Checking every task can avoid some stale-memory errors, but it adds work. This project examines that tradeoff using a small, reproducible simulation.

**Implementation status:** the six-policy simulator below is implemented. The newer **selective verification** research direction—deciding when to double-check memory—is a proposal, not an implemented or validated feature. See [the research roadmap](docs/selective-verification.md).

**Evidence:** 144,000 simulated decision records = 20 random seeds × 240 tasks × 6 policies × 5 scenarios. These are not distinct production tasks or real LLM calls. The simulator labels corrupted feedback as untrusted; zero errors with a trust gate therefore does not demonstrate autonomous detection of bad advice. No dollar savings have been measured.

A compact research companion for *Agentic Context Engineering under Policy Drift: Validity-Gated Playbooks for Operational Agents*. Python 3.10+, SQLite, no dependencies for the default experiment. Includes a research manuscript, measured pilot results, audit records and an optional local Ollama adapter.

This is an independent educational implementation inspired by [Zhang et al.'s ACE](https://arxiv.org/abs/2510.04618), **not the official ACE implementation or a reproduction of its benchmark scores**. The [official project](https://github.com/ace-agent/ace) is a separate codebase. No upstream source was copied.

## Business value and ROI

The business question is whether reusing valid experience saves more work than maintaining and checking that experience costs.

| Potential benefit | How to measure it |
| --- | --- |
| Less repeated investigation | Lookups, elapsed time and reviewer effort per task |
| Fewer obsolete operational actions | Consequential errors and recovery work |
| Lower total task cost | Model, verification, retry and review cost per successful task |

**Net benefit = avoided failure costs + saved investigation effort − added memory and validation costs.**

No financial ROI has been measured. The pilot uses assigned utility points. The roadmap proposes real-model experiments and selective checks; those results do not exist yet.

## Run in two minutes

After uploading the project, clone the repository and run the standard-library experiment. If you downloaded the ZIP, extract it, open a terminal in the `ace-context-lab` folder, and run the two Python commands below:

```bash
git clone https://github.com/achakraborty2024/ace-context-lab.git
cd ace-context-lab
python -m unittest discover -s tests -v
python -m ace_lab.run --out results/reproduce --seeds 20 --steps 240
```

The default mode makes **no LLM calls**. It deterministically simulates maintenance decisions and memory policies. Output directories must be new or empty. No installation, paid API, cloud credentials, real deployment, Jira or Symphony connection is needed.

Read `paper/research-paper.md`, open `results/pilot/report.html`, or inspect `results/pilot/summary.json`. The included results are simulation evidence only.

## Pilot results

![Simulation comparison across six memory policies and five scenarios](results/pilot/comparison.png)

| Finding | What it establishes |
| --- | --- |
| Clean feedback: scoped and gated match | Simple metadata filtering explains the measured benefit |
| Marked noisy feedback: 20.83% errors with scoped, 0% with gated | Rejecting feedback already labeled untrusted works in this simulator |
| Hidden changes: 2.50% errors for recency, scoped and gated | The initial stale actions are not prevented when the version does not change |

**144,000 means simulated decision records, not unique production tasks or LLM calls.** Read the [evidence guide](results/pilot/README.md), [summary](results/pilot/summary.json) and [limitations](paper/evidence-notes.md).

## What happens

Three fictional services (`api`, `worker`, `database`) require either serial or parallel maintenance. At the halfway point, policies flip in four scenarios. Agents see task scope and an advertised version, but never the required action before choosing. They can pay a simulated lookup cost to inspect the current rule and complete the task correctly. After scoring, feedback becomes available for future tasks.

| Mode | Retrieval | Learning |
|---|---|---|
| none | No memory; inspect | None |
| static | Latest service rule | Freeze after first 10% of tasks |
| recency | Latest service rule | Every feedback item |
| frequency | Most frequently observed service rule | Every feedback item |
| scoped | Latest service/region/version match | Every feedback item |
| gated | Same as scoped | Verified, supported feedback only |

All retrieving modes have a maximum of four bullets per request. The deterministic generator uses the first. These are transparent baselines, not implementations of full ACE, GEPA, Dynamic Cheatsheet or semantic RAG. `support` measures observed proposals, **not causal usefulness or success**.

## Scenarios

- `stationary`: stable rules, one region.
- `drift`: rule flips with a visible version increment.
- `mixed_scope`: opposite rules across two regions, plus visible drift.
- `noisy_feedback`: visible drift plus 20% corrupted proposals, explicitly marked untrusted by the simulator.
- `hidden_drift`: rule flips without changing the advertised version.

Correct direct action earns 1; wrong action earns -2; inspect earns `1 - lookup_cost` (default 0.7). Every inspect succeeds by assumption. These are synthetic utility units, not dollars or real operational risk estimates. A completed inspect is counted as successful task completion, but separately recorded as a lookup.

## Optional real language-model experiment

Install and start [Ollama](https://docs.ollama.com/), and download a model appropriate for your machine. Set its exact installed tag:

```bash
export ACE_OLLAMA_MODEL='YOUR_INSTALLED_MODEL_TAG'
python -m ace_lab.run --out results/reproduce-llm --seeds 1 --steps 24 \
  --scenarios drift --modes scoped gated \
  --model-command 'python -m ace_lab.ollama_worker'
```

This small trial can invoke the model up to 96 times (generator and reflector for 48 decisions). The included worker contacts only `127.0.0.1:11434`. Generation and reflection use the same model; deterministic curation prevents a model from minting trust or changing scope. The environment remains simulated. Real model execution **has not been performed** for this release; adapter contract tests use mocked subprocess responses.

`model_calls.json` records role inputs, outputs, model names and returned usage counts. Capture the model digest, Ollama version, hardware and decoding settings alongside results before publication. Latency includes cold model loading; compare warmed and cold runs separately. Token counts are reported by the server, not independently verified.

Important: an LLM may apply scope filtering on its own even in the recency baseline because scope metadata is visible. That is desirable evidence about the model; deterministic ranking outcomes must not be treated as predictions of LLM outcomes. Reflector calls are currently made even after static memory freezes, so this adapter is not a fair cost comparison for static mode. Run scoped/gated first, and revise call scheduling before comparative cost claims.

Use any other model via `--model-command`: one JSON request on stdin, one JSON object containing `action` on stdout. Role is `generator` or `reflector`. Allowed actions are `serial`, `parallel`, `inspect`. Invalid responses or timeouts stop the run; they are not silently counted as successful.

## Outputs and audit

- `traces.jsonl` (included as `traces.jsonl.gz`): every observation, action, chosen bullet ID, feedback, lookup and score.
- `per_seed.csv`: all/pre/post metrics for every seed and method.
- `summary.json`: post-change means and seed-bootstrap utility intervals.
- `paired.json`: paired differences between gated and each comparator.
- `manifest.json`: configuration, backend and SHA-256 hashes of Python modules.
- `playbooks.json`: final seed-0 playbooks.
- `*.sqlite` (included in `sqlite-audit.zip`): seed-0 memory and accepted/rejected update events for each scenario/method.

SQLite events support inspection, not automatic rollback or a distributed audit service. The current dataset has bounded rule cardinality; production pruning and conflict resolution are future work. The scalar support policy intentionally shows inertia and should not be deployed.

## Recreate figures and HTML

The simulation needs only the Python standard library. To regenerate the optional publication figure/report, install matplotlib in your own environment:

```bash
python -m pip install matplotlib
python scripts/render_results.py results/reproduce
```

## Project guide

| Location | Purpose |
| --- | --- |
| `ace_lab/` | Simulator, memory policies, CLI and optional model adapters |
| `tests/` | Unit tests and mocked adapter contracts |
| `paper/` | Manuscript, references and evidence boundaries |
| `docs/` | Proposed selective-verification research extension |
| `results/pilot/` | Measured simulation results and compressed evidence |
| `scripts/` | Figure and HTML report generation |

The included GitHub Actions workflow runs tests on Python 3.10 and 3.12. Contributions and independent replications are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Research boundaries

The trust flag and version metadata are simulator-controlled. Zero errors under those assumptions do not prove prompt-injection resistance. Hidden drift still causes errors. Independent held-out tasks, real LLM runs, stronger ACE baselines and human review are required before claims of general self-improvement. See the paper's limitations and research protocol.

Code: MIT license. Research manuscript: draft for author review. Cite the original ACE paper whenever discussing its method; cite this companion separately using its repository URL and the exact commit or release used.
