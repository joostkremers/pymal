import unittest

import pymal
from mal_types import *
import core
import mal_env as menv


class TestStep2(unittest.TestCase):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

    def test_eval1(self):
        ast = pymal.READ('(+ 1 2)')
        self.assertEqual(pymal.EVAL(ast, self.env), 3)

    def test_eval2(self):
        ast = pymal.READ('(+ 5 (* 2 3))')
        self.assertEqual(pymal.EVAL(ast, self.env), 11)

    def test_eval3(self):
        ast = pymal.READ('(- (+ 5 (* 2 3)) 3)')
        self.assertEqual(pymal.EVAL(ast, self.env), 8)

    def test_eval4(self):
        ast = pymal.READ('(/ (- (+ 515 (* 222 311)) 302) 27)')
        self.assertEqual(pymal.EVAL(ast, self.env), 2565)

    def test_eval5(self):
        ast = pymal.READ('(* -3 6)')
        self.assertEqual(pymal.EVAL(ast, self.env), -18)

    def test_eval6(self):
        ast = pymal.READ('(/ (- (+ 515 (* -222 311)) 296) 27)')
        self.assertEqual(pymal.EVAL(ast, self.env), -2549)

    def test_eval7(self):
        ast = pymal.READ('(abc 1 2 3)')
        self.assertIs(type(pymal.EVAL(ast, self.env)), MalError)

    def test_eval8(self):
        ast = pymal.READ('[1 2 (+ 1 2)]')
        self.assertEqual(pymal.EVAL(ast, self.env), MalVector([1, 2, 3]))

    def test_eval9(self):
        ast = pymal.READ('{"a" (+ 7 8)}')
        self.assertEqual(pymal.EVAL(ast, self.env), MalHash({"a": 15}))

    def test_eval10(self):
        ast = pymal.READ('{:a (+ 7 8)}')
        self.assertEqual(pymal.EVAL(ast, self.env),
                         pymal.READ('{:a 15}'))
