import unittest

import pymal
from mal_types import *
import core
import mal_env as menv


class TestStep3(unittest.TestCase):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

    def test_def(self):
        pymal.rep('(def! x 3)', self.env)
        ast = pymal.READ('x')
        self.assertEqual(pymal.EVAL(ast, self.env), 3)

        pymal.rep('(def! x 4)', self.env)
        self.assertEqual(pymal.EVAL(ast, self.env), 4)

        pymal.rep('(def! y (+ 1 7))', self.env)
        ast = pymal.READ('y')
        self.assertEqual(pymal.EVAL(ast, self.env), 8)

    def test_let(self):
        pymal.rep('(def! x 4)', self.env)
        ast = pymal.READ('(let* (z 9) z)')
        self.assertEqual(pymal.EVAL(ast, self.env), 9)

        ast = pymal.READ('(let* (x 9) x)')
        self.assertEqual(pymal.EVAL(ast, self.env), 9)

        ast = pymal.READ('x')
        self.assertEqual(pymal.EVAL(ast, self.env), 4)

        ast = pymal.READ('(let* (z (+ 2 3)) (+ 1 z))')
        self.assertEqual(pymal.EVAL(ast, self.env), 6)

        ast = pymal.READ('(let* (p (+ 2 3) q (+ 2 p)) (+ p q))')
        self.assertEqual(pymal.EVAL(ast, self.env), 12)

    def test_outer_env(self):
        pymal.rep('(def! a 4)', self.env)
        ast = pymal.READ('(let* (q 9) q)')
        self.assertEqual(pymal.EVAL(ast, self.env), 9)

        ast = pymal.READ('(let* (q 9) a)')
        self.assertEqual(pymal.EVAL(ast, self.env), 4)

        ast = pymal.READ('(let* (z 2) (let* (q 9) a))')
        self.assertEqual(pymal.EVAL(ast, self.env), 4)

        ast = pymal.READ('(let* (x 4) (def! a 5))')
        self.assertEqual(pymal.EVAL(ast, self.env), 5)

        ast = pymal.READ('a')
        self.assertEqual(pymal.EVAL(ast, self.env), 4)

    def test_let_vector(self):
        ast = pymal.READ('(let* [z 9] z)')
        self.assertEqual(pymal.EVAL(ast, self.env), 9)

        ast = pymal.READ('(let* [p (+ 2 3) q (+ 2 p)] (+ p q))')
        self.assertEqual(pymal.EVAL(ast, self.env), 12)

    def test_vector_evaluation(self):
        ast = pymal.READ('(let* (a 5 b 6) [3 4 a [b 7] 8])')
        self.assertEqual(pymal.EVAL(ast, self.env),
                         MalVector([3, 4, 5, [6, 7], 8]))
