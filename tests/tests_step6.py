from io import StringIO
from contextlib import redirect_stdout
import unittest

import pymal
from mal_types import *
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep6(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

        self.env.set("eval", MalBuiltin(pymal.mal_eval))
        self.env.set("swap!", MalBuiltin(pymal.mal_swap))

        pymal.rep('(def! load-file (fn* (f)'
                  '  (eval'
                  '    (read-string (str "(do " (slurp f) ")")))))',
                  self.env)
        # Set up a mock *ARGV*
        self.env.set("*ARGV*", MalList([]))
        # set repl_env for 'eval'
        pymal.repl_env = self.env

    def test_read_string(self):  # 38
        self.assertEval('(read-string "(1 2 (3 4) nil)")', self.env,
                        '(1 2 (3 4) nil)')
        self.assertEval('(read-string "(+ 2 3)")', self.env, '(+ 2 3)')
        self.assertEval('(read-string "7 ;; comment")', self.env, '7')
        self.assertEval('(read-string ";; comment")', self.env, '')
        self.assertEval('(eval (read-string "(+ 2 3)"))', self.env, '5')

    def test_slurp(self):  # 39
        self.assertEval('(slurp "tests/test.txt")',
                        self.env, r'"A line of text\n"')

    def test_load_file(self):  # 40
        pymal.rep('(load-file "tests/inc.mal")', self.env)
        self.assertEval('(inc1 7)', self.env, '8')
        self.assertEval('(inc2 7)', self.env, '9')
        self.assertEval('(inc3 9)', self.env, '12')

    def test_ARGV(self):  # 41
        self.assertEval('(list? *ARGV*)', self.env, 'true')
        self.assertEval('*ARGV*', self.env, '()')

    def test_atom(self):  # 42
        pymal.rep('(def! inc3 (fn* (a) (+ 3 a)))', self.env)
        self.assertEval('(def! a (atom 2))', self.env, '(atom 2)')
        self.assertEval('(atom? a)', self.env, 'true')
        self.assertEval('(atom? 1)', self.env, 'false')
        self.assertEval('(deref a)', self.env, '2')
        self.assertEval('(reset! a 3)', self.env, '3')
        self.assertEval('(deref a)', self.env, '3')
        self.assertEval('(swap! a inc3)', self.env, '6')
        self.assertEval('(deref a)', self.env, '6')
        self.assertEval('(swap! a (fn* (a) a))', self.env, '6')
        self.assertEval('(swap! a (fn* (a) (* 2 a)))', self.env, '12')
        self.assertEval('(swap! a (fn* (a b) (* a b)) 10)', self.env, '120')
        self.assertEval('(swap! a + 3)', self.env, '123')

    def test_swap_closure_interaction(self):  # 43
        pymal.rep('(def! inc-it (fn* (a) (+ 1 a)))', self.env)
        pymal.rep('(def! atm (atom 7))', self.env)
        pymal.rep('(def! f (fn* () (swap! atm inc-it)))', self.env)
        self.assertEval('(f)', self.env, '8')
        self.assertEval('(f)', self.env, '9')

    def test_comments_in_files(self):  # 44
        f = StringIO()
        with redirect_stdout(f):
            res = pymal.rep('(load-file "tests/incB.mal")', self.env)
        self.assertEqual(res, '"incB.mal return string"')
        self.assertEqual(f.getvalue(), '"incB.mal finished"\n')
        self.assertEval('(inc4 7)', self.env, '11')
        self.assertEval('(inc5 7)', self.env, '12')

    def test_map_across_multiple_lines(self):  # 45
        pymal.rep('(load-file "tests/incC.mal")', self.env)
        self.assertEval('mymap', self.env, '{"a" 1}')

    def test_at_reader_macro(self):  # 46
        pymal.rep('(def! atm (atom 9))', self.env)
        self.assertEval('@atm', self.env, '9')
