import json, os, subprocess, sys, tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from seasonseat.model import load_problem, ModelError
from seasonseat.planner import plan, verify
from seasonseat.report import build_report

class TestModel(unittest.TestCase):
    def test_basic(self):
        data = {"people":[{"id":"a"},{"id":"b"}],"seats":[{"id":"s1","row":0,"col":0,"quality":5},{"id":"s2","row":0,"col":1,"quality":3}],"events":2}
        p = load_problem(data)
        self.assertEqual(len(p.people),2)
        self.assertEqual(p.events,2)
    def test_events_invalid(self):
        with self.assertRaises(ModelError):
            load_problem({"people":[{"id":"a"}],"seats":[{"id":"s1","row":0,"col":0}],"events":0})
    def test_fewer_seats(self):
        with self.assertRaises(ModelError):
            load_problem({"people":[{"id":"a"},{"id":"b"}],"seats":[{"id":"s1","row":0,"col":0}],"events":1})
    def test_duplicate_person(self):
        with self.assertRaises(ModelError):
            load_problem({"people":[{"id":"a"},{"id":"a"}],"seats":[{"id":"s1","row":0,"col":0},{"id":"s2","row":0,"col":1}],"events":1})

class TestPlan(unittest.TestCase):
    def setUp(self):
        data = {"people":[{"id":"a"},{"id":"b"}],"seats":[{"id":"s1","row":0,"col":0,"quality":5},{"id":"s2","row":0,"col":1,"quality":3}],"events":2}
        self.problem = load_problem(data)
    def test_plan(self):
        r = plan(self.problem)
        self.assertEqual(r.status in ("optimal","feasible"), True)
        self.assertEqual(len(r.assignments),2)
        # no repeat
        a0 = set(r.assignments[0].values())
        a1 = set(r.assignments[1].values())
        # person a not same seat
        self.assertNotEqual(r.assignments[0]["a"], r.assignments[1]["a"])
    def test_verify(self):
        r = plan(self.problem)
        rep = build_report(self.problem, r)
        ok, errs = verify(self.problem, rep)
        self.assertTrue(ok, errs)

class TestCLI(unittest.TestCase):
    def test_demo(self):
        rc = subprocess.run([sys.executable,"-m","seasonseat","demo"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(rc.returncode, 0, rc.stderr+rc.stdout)

if __name__ == "__main__":
    unittest.main()
