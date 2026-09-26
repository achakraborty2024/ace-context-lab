import json
import sqlite3
import unittest
from dataclasses import asdict
from ace_lab.core import Feedback, Memory, Task, World
from ace_lab.run import trial

class LabTests(unittest.TestCase):
    def memory(self, mode):
        db=sqlite3.connect(':memory:'); self.addCleanup(db.close)
        return Memory(db,mode)

    def test_prediction_observation_excludes_label(self):
        task=World('drift',0,24).tasks[0]
        self.assertEqual(set(asdict(task)), {'step','service','region','version'})

    def test_cold_start_and_score_before_update(self):
        rows,_=trial('stationary',0,'gated',24)
        self.assertEqual(rows[0]['action'],'inspect')
        self.assertEqual(rows[0]['bullet_ids'],[])

    def test_scope_and_version_isolation(self):
        m=self.memory('gated')
        m.update(Task(0,'api','us',1),Feedback('serial',True,'sandbox_verifier'),2)
        self.assertEqual(m.retrieve(Task(1,'api','eu',1)),[])
        self.assertEqual(m.retrieve(Task(1,'api','us',2)),[])
        self.assertEqual(m.retrieve(Task(1,'api','us',1))[0]['action'],'serial')

    def test_reject_untrusted_and_forged_source(self):
        m=self.memory('gated'); t=Task(0,'api','us',1)
        m.update(t,Feedback('parallel',False,'unverified_log'),2)
        m.update(t,Feedback('parallel',True,'unverified_log'),2)
        self.assertEqual(m.snapshot(),[])
        self.assertEqual(m.db.execute('SELECT COUNT(*) FROM events').fetchone()[0],2)

    def test_upsert_preserves_unrelated_rules(self):
        m=self.memory('gated')
        for i,s in enumerate(('api','worker','api')):
            m.update(Task(i,s,'us',1),Feedback('serial',True,'sandbox_verifier'),5)
        self.assertEqual(len(m.snapshot()),2)
        self.assertEqual(m.snapshot()[0]['support'],2)

    def test_repeatability(self):
        self.assertEqual(trial('mixed_scope',7,'recency',36),trial('mixed_scope',7,'recency',36))

    def test_no_memory_lookup_utility(self):
        rows,_=trial('drift',0,'none',24)
        self.assertTrue(all(r['correct'] and r['utility']==.7 for r in rows))

    def test_visible_change_and_hidden_change(self):
        visible,_=trial('drift',0,'gated',240)
        hidden,_=trial('hidden_drift',0,'gated',240)
        self.assertEqual(sum(r['unsafe'] for r in visible),0)
        self.assertGreater(sum(r['unsafe'] for r in hidden),0)

    def test_noise_ablation(self):
        gated,_=trial('noisy_feedback',3,'gated',240)
        scoped,_=trial('noisy_feedback',3,'scoped',240)
        self.assertEqual(sum(r['unsafe'] for r in gated),0)
        self.assertGreater(sum(r['unsafe'] for r in scoped),0)

if __name__ == '__main__':
    unittest.main()
