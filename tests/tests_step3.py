import unittest

import pymal
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep3(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

    def test_def(self):  # 17
        pymal.rep('(def! x 3)', self.env)
        self.assertEval('x', self.env, '3')

        pymal.rep('(def! x 4)', self.env)
        self.assertEval('x', self.env, '4')

        pymal.rep('(def! y (+ 1 7))', self.env)
        self.assertEval('y', self.env, '8')

    def test_let(self):  # 18
        pymal.rep('(def! x 4)', self.env)
        self.assertEval('(let* (z 9) z)', self.env, '9')
        self.assertEval('(let* (x 9) x)', self.env, '9')
        self.assertEval('x', self.env, '4')
        self.assertEval('(let* (z (+ 2 3)) (+ 1 z))', self.env, '6')
        self.assertEval('(let* (p (+ 2 3) q (+ 2 p)) (+ p q))', self.env, '12')

    def test_outer_env(self):  # 19
        pymal.rep('(def! a 4)', self.env)
        self.assertEval('(let* (q 9) q)', self.env, '9')
        self.assertEval('(let* (q 9) a)', self.env, '4')
        self.assertEval('(let* (z 2) (let* (q 9) a))', self.env, '4')
        self.assertEval('(let* (x 4) (def! a 5))', self.env, '5')
        self.assertEval('a', self.env, '4')

    def test_let_vector(self):  # 20
        self.assertEval('(let* [z 9] z)', self.env, '9')
        self.assertEval('(let* [p (+ 2 3) q (+ 2 p)] (+ p q))',
                        self.env, '12')

    def test_vector_evaluation(self):  # 21
        self.assertEval('(let* (a 5 b 6) [3 4 a [b 7] 8])', self.env,
                        '[3 4 5 [6 7] 8]')
