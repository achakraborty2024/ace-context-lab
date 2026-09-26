from __future__ import annotations
import json
import random
import sqlite3
from dataclasses import asdict, dataclass

MODES = ('none', 'static', 'recency', 'frequency', 'scoped', 'gated')
SCENARIOS = ('stationary', 'drift', 'mixed_scope', 'noisy_feedback', 'hidden_drift')
ACTIONS = ('serial', 'parallel', 'inspect')

@dataclass(frozen=True)
class Task:
    step: int
    service: str
    region: str
    version: int

@dataclass(frozen=True)
class Feedback:
    action: str
    trusted: bool
    source: str

class World:
    """Private evaluator. Required actions never enter Task observations."""
    def __init__(self, scenario: str, seed: int, steps: int):
        if scenario not in SCENARIOS or steps < 12:
            raise ValueError('Unknown scenario or steps < 12')
        self.scenario, self.steps = scenario, steps
        rng = random.Random(seed)
        self.rules = {s: rng.choice(ACTIONS[:2]) for s in ('api', 'worker', 'database')}
        self.tasks, self.noise = [], []
        for i in range(steps):
            region = rng.choice(('us', 'eu')) if scenario == 'mixed_scope' else 'us'
            changed = i >= steps // 2 and scenario != 'stationary'
            version = 2 if changed and scenario != 'hidden_drift' else 1
            self.tasks.append(Task(i, rng.choice(tuple(self.rules)), region, version))
            self.noise.append(rng.random() < .2 if scenario == 'noisy_feedback' else False)

    def expected(self, task: Task) -> str:
        flip = (task.step >= self.steps // 2 and self.scenario != 'stationary')
        flip ^= task.region == 'eu'
        base = self.rules[task.service]
        return ACTIONS[1 - ACTIONS.index(base)] if flip else base

    def evaluate(self, task: Task, action: str, lookup_cost: float):
        if action not in ACTIONS:
            raise ValueError('Invalid action')
        expected = self.expected(task)
        correct = action == expected or action == 'inspect'
        utility = (1 - lookup_cost) if action == 'inspect' else (1 if correct else -2)
        # Corruption is an explicitly untrusted proposal, not a compromised verifier.
        proposed = ACTIONS[1 - ACTIONS.index(expected)] if self.noise[task.step] else expected
        feedback = Feedback(proposed, not self.noise[task.step],
                            'unverified_log' if self.noise[task.step] else 'sandbox_verifier')
        return correct, utility, feedback

class Memory:
    def __init__(self, connection: sqlite3.Connection, mode: str):
        if mode not in MODES:
            raise ValueError('Unknown mode')
        self.db, self.mode = connection, mode
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS bullets(
            id INTEGER PRIMARY KEY, service TEXT, region TEXT, version INTEGER,
            action TEXT, support INTEGER, last_step INTEGER, source TEXT,
            UNIQUE(service, region, version, action));
        CREATE TABLE IF NOT EXISTS events(
            step INTEGER, operation TEXT, payload TEXT);
        ''')

    def retrieve(self, task: Task, budget: int = 4):
        if self.mode == 'none':
            return []
        where, args = 'service=?', [task.service]
        if self.mode in ('scoped', 'gated'):
            where += ' AND region=? AND version=?'
            args += [task.region, task.version]
        order = 'support DESC, last_step DESC, id DESC' if self.mode == 'frequency' else 'last_step DESC, id DESC'
        return [dict(row) for row in self.db.execute(
            f'SELECT * FROM bullets WHERE {where} ORDER BY {order} LIMIT ?', args + [budget])]

    def update(self, task: Task, feedback: Feedback, warmup: int):
        if self.mode == 'none' or self.mode == 'static' and task.step >= warmup:
            return
        accepted = self.mode != 'gated' or feedback.trusted and feedback.source == 'sandbox_verifier'
        with self.db:
            self.db.execute('INSERT INTO events VALUES(?,?,?)',
                            (task.step, 'accept' if accepted else 'reject',
                             json.dumps({'task': asdict(task), 'feedback': asdict(feedback)}, sort_keys=True)))
            if accepted:
                self.db.execute('''INSERT INTO bullets(service,region,version,action,support,last_step,source)
                    VALUES(?,?,?,?,1,?,?) ON CONFLICT(service,region,version,action)
                    DO UPDATE SET support=support+1,last_step=excluded.last_step,source=excluded.source''',
                    (task.service, task.region, task.version, feedback.action, task.step, feedback.source))

    def snapshot(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM bullets ORDER BY id')]


def generate(task: Task, bullets: list[dict]) -> str:
    """Deterministic stand-in for a model; never accesses World or hidden rules."""
    return bullets[0]['action'] if bullets else 'inspect'
