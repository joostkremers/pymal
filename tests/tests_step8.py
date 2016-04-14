import unittest

import pymal
from mal_types import *
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep8(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

        # Add 'eval' and 'swap!' functions
        self.env.set("eval", MalBuiltin(pymal.mal_eval))
        self.env.set("swap!", MalBuiltin(pymal.mal_swap))
        # set repl_env for 'eval'
        pymal.repl_env = self.env

        # Add 'load-file' and use it to load the prelude
        pymal.rep('(def! load-file (fn* (f)'
                  '  (eval'
                  '    (read-string (str "(do " (slurp f) ")")))))',
                  self.env)
        pymal.rep('(load-file "prelude.mal")', self.env)

    def test_non_macro_function(self):  # 57
        self.assertEval('(not (= 1 1))', self.env, 'false')
        self.assertEval('(not (= 1 2))', self.env, 'true')

    def test_trivial_macros(self):  # 58
        pymal.rep('(defmacro! one (fn* () 1))', self.env)
        self.assertEval('(one)', self.env, '1')
        pymal.rep('(defmacro! two (fn* () 2))', self.env)
        self.assertEval('(two)', self.env, '2')

    def test_unless_macro(self):  # 59
        pymal.rep('(defmacro! unless (fn* (pred a b)'
                  '  `(if ~pred ~b ~a)))', self.env)
        self.assertEval('(unless false 7 8)', self.env, '7')
        self.assertEval('(unless true 7 8)', self.env, '8')

        pymal.rep('(defmacro! unless2 (fn* (pred a b)'
                  '  `(if (not ~pred) ~a ~b)))', self.env)
        self.assertEval('(unless2 false 7 8)', self.env, '7')
        self.assertEval('(unless2 true 7 8)', self.env, '8')

    def test_macroexpand(self):  # 60
        pymal.rep('(defmacro! unless2 (fn* (pred a b)'
                  '  `(if (not ~pred) ~a ~b)))', self.env)
        self.assertEval('(macroexpand (unless2 2 3 4))',
                        self.env, '(if (not 2) 3 4)')

    def test_evaluation_of_macro_result(self):  # 61
        pymal.rep('(defmacro! identity (fn* (x) x))', self.env)
        self.assertEval('(let* (a 123) (identity a))', self.env, '123')

    def test_nth_first_rest(self):  # 62
        self.assertEval("(nth '(1) 0)", self.env, '1')
        self.assertEval("(nth '(1 2) 1)", self.env, '2')
        pymal.rep('(def! x "x")', self.env)
        pymal.rep("(def! x (nth '(1 2) 2))", self.env)
        self.assertEval('x', self.env, '"x"')

        self.assertEval("(first '())", self.env, 'nil')
        self.assertEval("(first '(6))", self.env, '6')
        self.assertEval("(first '(7 8 9))", self.env, '7')

        self.assertEval("(rest '())", self.env, '()')
        self.assertEval("(rest '(6))", self.env, '()')
        self.assertEval("(rest '(7 8 9))", self.env, '(8 9)')

    def test_or_macro(self):  # 63
        self.assertEval('(or)', self.env, 'nil')
        self.assertEval('(or 1)', self.env, '1')
        self.assertEval('(or 1 2 3 4)', self.env, '1')
        self.assertEval('(or false 2)', self.env, '2')
        self.assertEval('(or false nil 3)', self.env, '3')
        self.assertEval('(or false nil false false nil 4)', self.env, '4')
        self.assertEval('(or false nil 3 false nil 4)', self.env, '3')
        self.assertEval('(or (or false 4))', self.env, '4')

    def test_cond_macro(self):  # 64
        self.assertEval('(cond)', self.env, 'nil')
        self.assertEval('(cond true 7)', self.env, '7')
        self.assertEval('(cond true 7 true 8)', self.env, '7')
        self.assertEval('(cond false 7 true 8)', self.env, '8')
        self.assertEval('(cond false 7 false 8 "else" 9)', self.env, '9')
        self.assertEval('(cond false 7 (= 2 2) 8 "else" 9)', self.env, '8')
        self.assertEval('(cond false 7 false 8 false 9)', self.env, 'nil')

    def test_EVAL_in_let(self):  # 65
        self.assertEval('(let* (x (or nil "yes")) x)', self.env, '"yes"')

    def test_nth_first_rest_with_vectors(self):  # 66
        self.assertEval('(nth [1] 0)', self.env, '1')
        self.assertEval('(nth [1 2] 1)', self.env, '2')

        pymal.rep('(def! x "x")', self.env)
        pymal.rep('(def! x (nth [1 2] 2))', self.env)
        self.assertEval('x', self.env, '"x"')
        self.assertEval('(first [])', self.env, 'nil')
        self.assertEval('(first nil)', self.env, 'nil')
        self.assertEval('(first [10])', self.env, '10')
        self.assertEval('(first [10 11 12])', self.env, '10')
        self.assertEval('(rest [])', self.env, '()')
        self.assertEval('(rest nil)', self.env, '()')
        self.assertEval('(rest [10])', self.env, '()')
        self.assertEval('(rest [10 11 12])', self.env, '(11 12)')

    def test_thread_first_macro(self):  # 67
        self.assertEval('(-> 7)', self.env, '7')
        self.assertEval('(-> (list 7 8 9) first)', self.env, '7')
        self.assertEval('(-> (list 7 8 9) (first))', self.env, '7')
        self.assertEval('(-> (list 7 8 9) first (+ 7))', self.env, '14')
        self.assertEval('(-> (list 7 8 9) rest (rest) first (+ 7))',
                        self.env, '16')

    def test_thread_last_macro(self):
        self.assertEval('(->> "L")', self.env, '"L"')
        self.assertEval('(->> "L" (str "A") (str "M"))', self.env, '"MAL"')
        self.assertEval('(->> [4]'
                        '  (concat [3]) (concat [2]) rest (concat [1]))',
                        self.env, '(1 3 4)')
