import unittest

import pymal
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep7(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

    def test_cons(self):  # 47
        self.assertEval('(cons 1 (list))', self.env, '(1)')
        self.assertEval('(cons 1 (list 2))', self.env, '(1 2)')
        self.assertEval('(cons 1 (list 2 3))', self.env, '(1 2 3)')
        self.assertEval('(cons (list 1) (list 2 3))', self.env, '((1) 2 3)')

        pymal.rep('(def! a (list 2 3))', self.env)
        self.assertEval('(cons 1 a)', self.env, '(1 2 3)')
        self.assertEval('a', self.env, '(2 3)')

    def test_concat(self):  # 48
        self.assertEval('(concat)', self.env, '()')
        self.assertEval('(concat (list 1 2))', self.env, '(1 2)')
        self.assertEval('(concat (list 1 2) (list 3 4))', self.env,
                        '(1 2 3 4)')
        self.assertEval('(concat (list 1 2) (list 3 4) (list 5 6))',
                        self.env, '(1 2 3 4 5 6)')
        self.assertEval('(concat (concat))', self.env, '()')

        pymal.rep('(def! a (list 1 2))', self.env)
        pymal.rep('(def! b (list 3 4))', self.env)
        self.assertEval('(concat a b (list 5 6))', self.env, '(1 2 3 4 5 6)')
        self.assertEval('a', self.env, '(1 2)')
        self.assertEval('b', self.env, '(3 4)')

    def test_regular_quote(self):  # 49
        self.assertEval("(quote 7)", self.env, '7')
        self.assertEval("'7", self.env, '7')
        self.assertEval("(quote (1 2 3))", self.env, '(1 2 3)')
        self.assertEval("'(1 2 3)", self.env, '(1 2 3)')
        self.assertEval("(quote (1 2 (3 4)))", self.env, '(1 2 (3 4))')
        self.assertEval("'(1 2 (3 4))", self.env, '(1 2 (3 4))')

    def test_quasiquote(self):  # 50
        self.assertEval('(quasiquote 7)', self.env, "7")
        self.assertEval('`7', self.env, "7")
        self.assertEval('(quasiquote (1 2 3))', self.env, "(1 2 3)")
        self.assertEval('`(1 2 3)', self.env, "(1 2 3)")
        self.assertEval('(quasiquote (1 2 (3 4)))', self.env, "(1 2 (3 4))")
        self.assertEval('`(1 2 (3 4))', self.env, "(1 2 (3 4))")
        self.assertEval('(quasiquote (nil))', self.env, "(nil)")
        self.assertEval('`(nil)', self.env, "(nil)")

    def test_unquote(self):  # 51
        self.assertEval("`~7", self.env, '7')
        self.assertEval("(def! a 8)", self.env, '8')
        self.assertEval("`a", self.env, 'a')
        self.assertEval("`~a", self.env, '8')
        self.assertEval("`(1 a 3)", self.env, '(1 a 3)')
        self.assertEval("`(1 ~a 3)", self.env, '(1 8 3)')
        self.assertEval('(def! b \'(1 "b" "d"))', self.env, '(1 "b" "d")')
        self.assertEval("`(1 b 3)", self.env, '(1 b 3)')
        self.assertEval("`(1 ~b 3)", self.env, '(1 (1 "b" "d") 3)')

    def test_splice_unquote(self):  # 52
        self.assertEval('(def! c \'(1 "b" "d"))', self.env, '(1 "b" "d")')
        self.assertEval('`(1 c 3)', self.env, '(1 c 3)')
        self.assertEval('`(1 ~@c 3)', self.env, '(1 1 "b" "d" 3)')

    def test_symbol_equality(self):  # 53
        self.assertEval('(= \'abc \'abc)', self.env, 'true')
        self.assertEval('(= \'abc \'abcd)', self.env, 'false')
        self.assertEval('(= \'abc "abc")', self.env, 'false')
        self.assertEval('(= "abc" \'abc)', self.env, 'false')
        self.assertEval('(= "abc" (str \'abc))', self.env, 'true')
        self.assertEval('(= \'abc nil)', self.env, 'false')
        self.assertEval('(= nil \'abc)', self.env, 'false')

    def test_cons_with_vectors(self):  # 54
        self.assertEval('(cons [1] [2 3])', self.env, '([1] 2 3)')
        self.assertEval('(cons 1 [2 3])', self.env, '(1 2 3)')
        self.assertEval('(concat [1 2] (list 3 4) [5 6])', self.env,
                        '(1 2 3 4 5 6)')

    def test_unquote_with_vectors(self):  # 55
        self.assertEval('(def! a 8)', self.env, '8')
        self.assertEval('`[1 a 3]', self.env, '(1 a 3)')

    def test_splice_unquote_with_vectors(self):  # 56
        self.assertEval('(def! c \'(1 "b" "d"))', self.env, '(1 "b" "d")')
        self.assertEval("`[1 ~@c 3]", self.env, '(1 1 "b" "d" 3)')
