from io import StringIO
from contextlib import redirect_stdout
import unittest

import pymal
from mal_types import *
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep4(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

    def test_list_functions(self):  # 22
        self.assertEval('(list)', self.env, '()')
        self.assertEval('(list? (list))', self.env, 'true')
        self.assertEval('(empty? (list))', self.env, 'true')
        self.assertEval('(empty? (list 1))', self.env, 'false')
        self.assertEval('(list 1 2 3)', self.env, '(1 2 3)')
        self.assertEval('(count (list 1 2 3))', self.env, '3')
        self.assertEval('(count (list))', self.env, '0')
        self.assertEval('(count nil)', self.env, '0')
        self.assertEval('(if (> (count (list 1 2 3)) 3)' ' "yes" "no")',
                        self.env, '"no"')
        self.assertEval('(if (>= (count (list 1 2 3)) 3)' ' "yes" "no")',
                        self.env, '"yes"')

    def test_if_form(self):  # 23
        self.assertEval('(if true 7 8)', self.env, '7')
        self.assertEval('(if false 7 8)', self.env, '8')
        self.assertEval('(if true (+ 1 7) (+ 1 8))', self.env, '8')
        self.assertEval('(if false (+ 1 7) (+ 1 8))', self.env, '9')
        self.assertEval('(if nil 7 8)', self.env, '8')
        self.assertEval('(if "" 7 8)', self.env, '7')
        self.assertEval('(if (list) 7 8)', self.env, '7')
        self.assertEval('(if (list 1 2 3) 7 8)', self.env, '7')
        self.assertEval('(= (list) nil)', self.env, 'false')

    def test_if_form_one_way(self):  # 24
        self.assertEval('(if false (+ 1 7))', self.env, 'nil')
        self.assertEval('(if nil 8 7)', self.env, '7')
        self.assertEval('(if true (+ 1 7))', self.env, '8')

    def test_basic_conditionals(self):  # 25
        self.assertEval('(= 2 1)', self.env, 'false')
        self.assertEval('(= 1 1)', self.env, 'true')
        self.assertEval('(= 1 2)', self.env, 'false')
        self.assertEval('(= 1 (+ 1 1))', self.env, 'false')
        self.assertEval('(= 2 (+ 1 1))', self.env, 'true')
        self.assertEval('(= nil 1)', self.env, 'false')
        self.assertEval('(= nil nil)', self.env, 'true')
        self.assertEval('(> 2 1)', self.env, 'true')
        self.assertEval('(> 1 1)', self.env, 'false')
        self.assertEval('(> 1 2)', self.env, 'false')
        self.assertEval('(>= 2 1)', self.env, 'true')
        self.assertEval('(>= 1 1)', self.env, 'true')
        self.assertEval('(>= 1 2)', self.env, 'false')
        self.assertEval('(< 2 1)', self.env, 'false')
        self.assertEval('(< 1 1)', self.env, 'false')
        self.assertEval('(< 1 2)', self.env, 'true')
        self.assertEval('(<= 2 1)', self.env, 'false')
        self.assertEval('(<= 1 1)', self.env, 'true')
        self.assertEval('(<= 1 2)', self.env, 'true')

    def test_equality(self):  # 26
        self.assertEval('(= 1 1)', self.env, 'true')
        self.assertEval('(= 0 0)', self.env, 'true')
        self.assertEval('(= 1 0)', self.env, 'false')
        self.assertEval('(= "" "")', self.env, 'true')
        self.assertEval('(= "abc" "")', self.env, 'false')
        self.assertEval('(= "" "abc")', self.env, 'false')
        self.assertEval('(= "abc" "def")', self.env, 'false')
        self.assertEval('(= (list) (list))', self.env, 'true')
        self.assertEval('(= (list 1 2) (list 1 2))', self.env, 'true')
        self.assertEval('(= (list 1) (list))', self.env, 'false')
        self.assertEval('(= (list) (list 1))', self.env, 'false')
        self.assertEval('(= 0 (list))', self.env, 'false')
        self.assertEval('(= (list) 0)', self.env, 'false')
        self.assertEval('(= (list) "")', self.env, 'false')
        self.assertEval('(= "" (list))', self.env, 'false')

    def test_builtin_and_user_functions(self):  # 27
        self.assertEval('(+ 1 2)', self.env, '3')
        self.assertEval('( (fn* (a b) (+ a b)) 3 4)', self.env, '7')
        self.assertEval('( (fn* () 4) )', self.env, '4')
        self.assertEval('( (fn* (f x) (f x)) (fn* (a) (+ 1 a)) 7)',
                        self.env, '8')

    def test_closures(self):  # 28
        self.assertEval('( ( (fn* (a) (fn* (b) (+ a b))) 5) 7)',
                        self.env, '12')
        pymal.rep('(def! gen-plus5 (fn* () (fn* (b) (+ 5 b))))', self.env)
        pymal.rep('(def! plus5 (gen-plus5))', self.env)
        self.assertEval('(plus5 7)', self.env, '12')

    def test_variable_length_arguments(self):  # 29
        self.assertEval('( (fn* (& more) (count more)) 1 2 3)', self.env, '3')
        self.assertEval('( (fn* (& more) (list? more)) 1 2 3)',
                        self.env, 'true')
        self.assertEval('( (fn* (& more) (count more)) 1)', self.env, '1')
        self.assertEval('( (fn* (& more) (count more)) )', self.env, '0')
        self.assertEval('( (fn* (& more) (list? more)) )', self.env, 'true')
        self.assertEval('( (fn* (a & more) (count more)) 1 2 3)',
                        self.env, '2')
        self.assertEval('( (fn* (a & more) (count more)) 1)', self.env, '0')
        self.assertEval('( (fn* (a & more) (list? more)) 1)', self.env, 'true')

    def test_not(self):  # 30
        pymal.rep("(def! not (fn* (a) (if a false true)))", self.env)

        self.assertEval('(not false)', self.env, 'true')
        self.assertEval('(not true)', self.env, 'false')
        self.assertEval('(not "a")', self.env, 'false')
        self.assertEval('(not 0)', self.env, 'false')

    def test_do(self):  # 31
        f = StringIO()
        with redirect_stdout(f):
            res = pymal.rep('(do (prn "prn output1"))', self.env)
        self.assertEqual(res, 'nil')
        self.assertEqual(f.getvalue(), '"prn output1"\n')

        g = StringIO()
        with redirect_stdout(g):
            res = pymal.rep('(do (prn "prn output2") 7)', self.env)
        self.assertEqual(res, '7')
        self.assertEqual(g.getvalue(), '"prn output2"\n')

        h = StringIO()
        with redirect_stdout(h):
            res = pymal.rep('(do'
                            '  (prn "prn output1")'
                            '  (prn "prn output2")'
                            '  (+ 1 2))', self.env)
        self.assertEqual(res, '3')
        self.assertEqual(h.getvalue(), '"prn output1"\n"prn output2"\n')

        self.assertEval('(do (def! a 6) 7 (+ a 8))', self.env, '14')
        self.assertEval('a', self.env, '6')

    def test_recursive_sumdown(self):  # 32
        pymal.rep('(def! sumdown (fn* (N)'
                  '  (if (> N 0)'
                  '      (+ N (sumdown (- N 1)))'
                  '    0)))', self.env)
        self.assertEval('(sumdown 1)', self.env, '1')
        self.assertEval('(sumdown 2)', self.env, '3')
        self.assertEval('(sumdown 6)', self.env, '21')

    def test_recursive_fibonacci(self):  # 33
        pymal.rep('(def! fib (fn* (N)'
                  '  (if (= N 0)'
                  '      1'
                  '    (if (= N 1)'
                  '        1'
                  '      (+ (fib (- N 1)) (fib (- N 2)))))))',
                  self.env)
        self.assertEval('(fib 1)', self.env, '1')
        self.assertEval('(fib 2)', self.env, '2')
        self.assertEval('(fib 4)', self.env, '5')
        self.assertEval('(fib 10)', self.env, '89')
