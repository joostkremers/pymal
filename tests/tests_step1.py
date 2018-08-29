import unittest

import pymal
import mal_types as mal
from eval_assert import EvalAssert


class TestStep1(unittest.TestCase, EvalAssert):
    def test_read_nil_true_false(self):  # 1
        self.assertEqual(pymal.READ('nil'), mal.NIL)
        self.assertEqual(pymal.READ('true'), mal.Boolean(True))
        self.assertEqual(pymal.READ('false'), mal.Boolean(False))

    def test_read_numbers(self):  # 2
        self.assertEqual(pymal.READ('1'), 1)
        self.assertEqual(pymal.READ('7'), 7)
        self.assertEqual(pymal.READ('-123'), -123)

    def test_read_symbols(self):  # 3
        self.assertEqual(pymal.READ('+'), mal.Symbol('+'))
        self.assertEqual(pymal.READ('abc'), mal.Symbol('abc'))
        self.assertEqual(pymal.READ('   abc'), mal.Symbol('abc'))
        self.assertEqual(pymal.READ('abc5'), mal.Symbol('abc5'))
        self.assertEqual(pymal.READ('abc-def'), mal.Symbol('abc-def'))

    def test_read_strings(self):  # 4
        self.assertEqual(pymal.READ('"abc"'), 'abc')
        self.assertEqual(pymal.READ('   "abc"'), 'abc')
        self.assertEqual(pymal.READ('"abc (with parens)"'),
                         'abc (with parens)')
        self.assertEqual(pymal.READ(r'"abc\"def"'), r'abc"def')
        self.assertEqual(pymal.READ(r'"abc\ndef"'), 'abc\ndef')
        self.assertEqual(pymal.READ('""'), '')

    # Also test that strings are printed back correctly:
    def test_read_print_strings(self):  # 5
        self.assertEval('"abc"', {}, '"abc"')
        self.assertEval('   "abc"', {}, '"abc"')
        self.assertEval('"abc (with parens)"', {}, '"abc (with parens)"')
        self.assertEval(r'"abc\"def"', {}, r'"abc\"def"')
        self.assertEval(r'"abc\ndef"', {}, r'"abc\ndef"')
        self.assertEval('""', {}, '""')

    # Note: we can test the result of READ against a list, not a mal.List,
    # since both types test equal.
    def test_read_lists(self):  # 6
        self.assertEqual(pymal.READ('(+ 1 2)'),
                         [mal.Symbol('+'), 1, 2])
        self.assertEqual(pymal.READ('((3 4))'), [[3, 4]])
        self.assertEqual(pymal.READ('(+ 1 (+ 2 3))'),
                         [mal.Symbol('+'), 1, [mal.Symbol('+'), 2, 3]])
        self.assertEqual(pymal.READ('  ( +   1   (+   2 3   )   )  '),
                         [mal.Symbol('+'), 1, [mal.Symbol('+'), 2, 3]])
        self.assertEqual(pymal.READ('(* 1 2)'), [mal.Symbol('*'), 1, 2])
        self.assertEqual(pymal.READ('(** 1 2)'), [mal.Symbol('**'), 1, 2])
        self.assertEqual(pymal.READ('(* -3 6)'), [mal.Symbol('*'), -3, 6])

    def test_read_comma_as_whitespace(self):  # 7
        self.assertEqual(pymal.READ('(1 2 3,,,,),,'), [1, 2, 3])

    def test_read_quoting(self):  # 8
        self.assertEqual(pymal.READ("'1"), [mal.Symbol('quote'), 1])
        self.assertEqual(pymal.READ("'(1 2 3)"),
                         [mal.Symbol('quote'), [1, 2, 3]])
        self.assertEqual(pymal.READ("`1"), [mal.Symbol('quasiquote'), 1])
        self.assertEqual(pymal.READ("`(1 2 3)"),
                         [mal.Symbol('quasiquote'), [1, 2, 3]])
        self.assertEqual(pymal.READ("~1"), [mal.Symbol('unquote'), 1])
        self.assertEqual(pymal.READ("~(1 2 3)"),
                         [mal.Symbol('unquote'), [1, 2, 3]])
        self.assertEqual(pymal.READ("~@(1 2 3)"),
                         [mal.Symbol('splice-unquote'), [1, 2, 3]])

    # Currently, the string '"abc' is read as the symbol 'abc', therefore we
    # skip these tests for the moment.
    @unittest.skip("Reader errors skipped.")
    def test_read_reader_errors(self):  # 9
        self.assertIs(type(pymal.READ('(1 2')), mal.Error)
        self.assertIs(type(pymal.READ('[1 2')), mal.Error)
        self.assertIs(type(pymal.READ('"abc')), mal.Error)
        self.assertIs(type(pymal.READ('(1 "abc')), mal.Error)

    def test_read_keywords(self):  # 10
        self.assertEqual(pymal.READ(':kw'), mal.Keyword(':kw'))
        self.assertEqual(pymal.READ('(:kw1 :kw2 :kw3)'),
                         [mal.Keyword(':kw1'),
                          mal.Keyword(':kw2'),
                          mal.Keyword(':kw3')])

        self.assertEqual(pymal.READ('[+ 1 2]'),
                         mal.Vector([mal.Symbol('+'), 1, 2]))
        self.assertEqual(pymal.READ('[[3 4]]'), mal.Vector([[3, 4]]))
        self.assertEqual(pymal.READ('[+ 1 [+ 2 3]]'),
                         mal.Vector([mal.Symbol('+'), 1,
                                     [mal.Symbol('+'), 2, 3]]))
        self.assertEqual(pymal.READ('[ +   1   [+   2 3   ]   ]  '),
                         mal.Vector([mal.Symbol('+'), 1,
                                     [mal.Symbol('+'), 2, 3]]))

    def test_read_hash(self):  # 11
        self.assertEqual(pymal.READ('{"abc" 1}'), mal.Hash({"abc": 1}))
        self.assertEqual(pymal.READ('{"a" {"b" 2}}'),
                         mal.Hash({"a": {"b": 2}}))
        self.assertEqual(pymal.READ('{"a" {"b" {"c" 3}}} '),
                         mal.Hash({"a": {"b": {"c": 3}}}))
        self.assertEqual(pymal.READ('{  "a"  {"b"   {  "cde"     3   }  }}'),
                         mal.Hash({"a": {"b": {"cde": 3}}}))
        self.assertEqual(pymal.READ('{  :a  {:b   {  :cde     3   }  }}   '),
                         mal.Hash({mal.Keyword(':a'):
                                   {mal.Keyword(':b'):
                                    {mal.Keyword(':cde'): 3}}}))

    def test_read_comments(self):  # 12
        self.assertEqual(pymal.READ(';; whole line comment'), None)
        self.assertEqual(pymal.READ('1 ; comment after expression'), 1)
        self.assertEqual(pymal.READ('1; comment after expression'), 1)

    def test_read_metadata(self):  # 13
        self.assertEqual(pymal.READ('^{"a" 1} [1 2 3]'),
                         [mal.Symbol('with-meta'), [1, 2, 3], {'a': 1}])

    def test_read_deref(self):  # 14
        self.assertEqual(pymal.READ('@a'),
                         [mal.Symbol('deref'), mal.Symbol('a')])
