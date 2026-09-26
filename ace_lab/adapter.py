"""Optional external model adapter; no API credentials required by the simulator."""
import json
import shlex
import subprocess
from dataclasses import asdict
from .core import ACTIONS, Feedback

class CommandModel:
    def __init__(self, command: str):
        self.argv = shlex.split(command)
        if not self.argv:
            raise ValueError('Empty model command')
        self.calls = []

    def call(self, payload):
        # Explicit user-supplied executable, never shell=True; stdout is JSON only.
        result = subprocess.run(self.argv, input=json.dumps(payload), text=True,
                                capture_output=True, timeout=120, check=True)
        response = json.loads(result.stdout)
        if not isinstance(response, dict) or response.get('action') not in ACTIONS:
            raise ValueError('Model must return a valid JSON action')
        self.calls.append({'request': payload, 'response': response})
        return response

    def generate(self, task, bullets):
        return self.call({'role': 'generator', 'task': asdict(task), 'playbook': bullets,
                          'allowed_actions': ACTIONS,
                          'instruction': 'Choose the applicable maintenance action. If evidence is insufficient, inspect.'})['action']

    def reflect(self, task, feedback):
        response = self.call({'role': 'reflector', 'task': asdict(task),
                              'feedback': asdict(feedback),
                              'instruction': 'Extract the reusable serial or parallel rule supported by feedback.'})
        # Model cannot mint trust or overwrite task scope. Unsupported proposals are rejected by gated mode.
        supported = response['action'] == feedback.action and response['action'] != 'inspect'
        if response['action'] == 'inspect':
            return None
        return Feedback(response['action'], feedback.trusted and supported,
                        feedback.source if supported else 'unsupported_reflection')
