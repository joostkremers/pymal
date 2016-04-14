import unittest

import pymal
from mal_types import *
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep2(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

    def test_eval(self):  # 15
        self.assertEval('(+ 1 2)', self.env, '3')
        self.assertEval('(+ 5 (* 2 3))', self.env, '11')
        self.assertEval('(- (+ 5 (* 2 3)) 3)', self.env, '8')
        self.assertEval('(/ (- (+ 515 (* 222 311)) 302) 27)', self.env, '2565')
        self.assertEval('(* -3 6)', self.env, '-18')
        self.assertEval('(/ (- (+ 515 (* -222 311)) 296) 27)',
                        self.env, '-2549')
        self.assertEval('[1 2 (+ 1 2)]', self.env, '[1 2 3]')
        self.assertEval('{"a" (+ 7 8)}', self.env, '{"a" 15}')
        self.assertEval('{:a (+ 7 8)}', self.env, '{:a 15}')

    def test_eval_error(self):  # 16
        ast = pymal.READ('(abc 1 2 3)')
        self.assertIs(type(pymal.EVAL(ast, self.env)), MalError)
