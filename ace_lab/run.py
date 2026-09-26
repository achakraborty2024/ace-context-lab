from __future__ import annotations
import argparse
import csv
import hashlib
import json
import platform
import random
import sqlite3
import statistics
from dataclasses import asdict
from pathlib import Path
from .adapter import CommandModel
from .core import MODES, SCENARIOS, Memory, World, generate


def trial(scenario, seed, mode, steps=240, lookup_cost=.3, db_path=':memory:', model=None):
    world = World(scenario, seed, steps)
    db = sqlite3.connect(db_path)
    memory = Memory(db, mode)
    records = []
    try:
        for task in world.tasks:
            bullets = memory.retrieve(task)
            action = model.generate(task, bullets) if model else generate(task, bullets)
            correct, utility, feedback = world.evaluate(task, action, lookup_cost)
            # Score first, then reflect/update: no current-answer leakage to the generator.
            records.append({'scenario': scenario, 'seed': seed, 'mode': mode, **asdict(task),
                            'action': action, 'correct': int(correct), 'utility': utility,
                            'lookup': int(action == 'inspect'), 'unsafe': int(not correct),
                            'bullet_ids': [b['id'] for b in bullets],
                            'context_bytes': len(json.dumps(bullets).encode()),
                            'feedback': asdict(feedback)})
            proposal = model.reflect(task, feedback) if model and mode != 'none' else feedback
            if proposal is not None:
                memory.update(task, proposal, warmup=steps // 10)
        return records, memory.snapshot()
    finally:
        db.close()


def bootstrap(values, seed=9281, repeats=2000):
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(repeats))
    return [means[int(.025 * repeats)], means[int(.975 * repeats)]]


def main():
    p = argparse.ArgumentParser(description='Controlled memory simulation; optional external LLM adapter.')
    p.add_argument('--out', type=Path, default=Path('results/reproduce'))
    p.add_argument('--seeds', type=int, default=20)
    p.add_argument('--steps', type=int, default=240)
    p.add_argument('--lookup-cost', type=float, default=.3)
    p.add_argument('--scenarios', nargs='+', choices=SCENARIOS, default=list(SCENARIOS))
    p.add_argument('--modes', nargs='+', choices=MODES, default=list(MODES))
    p.add_argument('--model-command', help='Executable reading one JSON request and writing one JSON response')
    args = p.parse_args()
    if args.seeds < 1 or args.steps < 12 or not 0 <= args.lookup_cost <= 1:
        p.error('Require seeds >= 1, steps >= 12, and lookup cost in [0,1]')
    if args.out.exists() and any(args.out.iterdir()):
        p.error('Output directory must be empty: preserve old experiment records')
    args.out.mkdir(parents=True, exist_ok=True)
    per_seed, examples = [], {}
    model = CommandModel(args.model_command) if args.model_command else None
    with (args.out / 'traces.jsonl').open('w') as trace:
        for scenario in args.scenarios:
            for seed in range(args.seeds):
                for mode in args.modes:
                    db_path = str(args.out / f'{scenario}-{mode}.sqlite') if seed == 0 else ':memory:'
                    records, snapshot = trial(scenario, seed, mode, args.steps, args.lookup_cost, db_path, model)
                    for record in records:
                        trace.write(json.dumps(record, sort_keys=True) + '\n')
                    if seed == 0:
                        examples[f'{scenario}/{mode}'] = snapshot
                    for phase, subset in (('all', records), ('pre', records[:args.steps//2]), ('post', records[args.steps//2:])):
                        per_seed.append({'scenario': scenario, 'seed': seed, 'mode': mode, 'phase': phase,
                                         **{k: statistics.mean(r[k] for r in subset)
                                            for k in ('correct', 'utility', 'lookup', 'unsafe', 'context_bytes')}})
    summary = []
    for scenario in args.scenarios:
        for mode in args.modes:
            rows = [r for r in per_seed if r['scenario'] == scenario and r['mode'] == mode and r['phase'] == 'post']
            summary.append({'scenario': scenario, 'mode': mode,
                            **{k: statistics.mean(r[k] for r in rows) for k in ('correct','utility','lookup','unsafe','context_bytes')},
                            'utility_ci95': bootstrap([r['utility'] for r in rows])})
    paired = []
    if 'gated' in args.modes:
        for scenario in args.scenarios:
            index = {(r['mode'],r['seed']): r['utility'] for r in per_seed if r['scenario']==scenario and r['phase']=='post'}
            for mode in args.modes:
                if mode == 'gated':
                    continue
                diffs = [index['gated',s] - index[mode,s] for s in range(args.seeds)]
                paired.append({'scenario':scenario,'comparison':f'gated - {mode}',
                               'utility_delta':statistics.mean(diffs),'ci95':bootstrap(diffs)})
    for name, value in [('summary.json',summary),('paired.json',paired),('playbooks.json',examples)]:
        (args.out/name).write_text(json.dumps(value,indent=2)+'\n')
    with (args.out/'per_seed.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(per_seed[0])); w.writeheader(); w.writerows(per_seed)
    manifest = {'backend':'external-command' if model else 'deterministic-simulation',
                'python':platform.python_version(),'seeds':list(range(args.seeds)), 'steps':args.steps,
                'lookup_cost':args.lookup_cost,'scenarios':args.scenarios,'modes':args.modes,
                'model_command':args.model_command,'notes':'No LLM evidence unless an external model command was configured.',
                'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    if model:
        (args.out/'model_calls.json').write_text(json.dumps(model.calls,indent=2)+'\n')
    print('scenario         mode       post utility    unsafe %    lookup %')
    for r in summary:
        print(f"{r['scenario']:16} {r['mode']:10} {r['utility']:12.3f} {100*r['unsafe']:11.2f} {100*r['lookup']:11.2f}")

if __name__ == '__main__':
    main()
