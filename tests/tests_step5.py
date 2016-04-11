import unittest

import pymal
from mal_types import *
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep5(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

    def test_tco(self):
        pymal.rep('(def! sum2 (fn* (n acc)'
                  '  (if (= n 0)'
                  '    acc'
                  '    (sum2 (- n 1) (+ n acc)))))', self.env)
        self.assertEval('(sum2 10 0)', self.env, '55')
        pymal.rep('(def! res2 nil)', self.env)
        pymal.rep('(def! res2 (sum2 10000 0))', self.env)
        self.assertEval('res2', self.env, '50005000')

    def test_multiple_recursive_tco(self):
        pymal.rep('(def! foo (fn* (n)'
                  '  (if (= n 0)'
                  '    0'
                  '    (bar (- n 1)))))', self.env)
        pymal.rep('(def! bar (fn* (n)'
                  '  (if (= n 0)'
                  '    0'
                  '    (foo (- n 1)))))', self.env)
        self.assertEval('(foo 10000)', self.env, '0')

    def test_do_under_tco(self):
        self.assertEval('(do (do 1 2))', self.env, '2')

    def test_vector_params(self):
        pymal.rep('(def! g (fn* [] 78))', self.env)
        self.assertEval('(g)', self.env, '78')
        pymal.rep('(def! g (fn* [a] (+ a 78)))', self.env)
        self.assertEval('(g 3)', self.env, '81')
