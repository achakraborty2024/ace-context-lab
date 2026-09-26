import json
import subprocess
import unittest
from unittest.mock import patch
from ace_lab.adapter import CommandModel
from ace_lab.core import Feedback, Task

class AdapterTests(unittest.TestCase):
    @patch('ace_lab.adapter.subprocess.run')
    def test_generator_payload_and_json(self, run):
        run.return_value=subprocess.CompletedProcess([],0,stdout='{"action":"inspect"}')
        model=CommandModel('python worker.py')
        self.assertEqual(model.generate(Task(1,'api','us',2),[]),'inspect')
        payload=json.loads(run.call_args.kwargs['input'])
        self.assertNotIn('expected',payload)
        self.assertNotIn('feedback',payload)
        self.assertEqual(len(model.calls),1)

    @patch('ace_lab.adapter.subprocess.run')
    def test_model_cannot_mint_trust(self, run):
        run.return_value=subprocess.CompletedProcess([],0,stdout='{"action":"parallel","trusted":true}')
        model=CommandModel('python worker.py')
        feedback=model.reflect(Task(0,'api','us',1),Feedback('serial',True,'sandbox_verifier'))
        self.assertFalse(feedback.trusted)
        self.assertEqual(feedback.source,'unsupported_reflection')

    @patch('ace_lab.adapter.subprocess.run')
    def test_invalid_action_fails(self, run):
        run.return_value=subprocess.CompletedProcess([],0,stdout='{"action":"delete"}')
        with self.assertRaises(ValueError):
            CommandModel('python worker.py').call({})
