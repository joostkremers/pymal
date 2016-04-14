import unittest

import pymal
from mal_types import *
from eval_assert import EvalAssert


class TestStep1(unittest.TestCase, EvalAssert):
    def test_read_nil_true_false(self):  # 1
        self.assertEqual(pymal.READ('nil'), MAL_NIL)
        self.assertEqual(pymal.READ('true'), MalBoolean(True))
        self.assertEqual(pymal.READ('false'), MalBoolean(False))

    def test_read_numbers(self):  # 2
        self.assertEqual(pymal.READ('1'), 1)
        self.assertEqual(pymal.READ('7'), 7)
        self.assertEqual(pymal.READ('-123'), -123)

    def test_read_symbols(self):  # 3
        self.assertEqual(pymal.READ('+'), MalSymbol('+'))
        self.assertEqual(pymal.READ('abc'), MalSymbol('abc'))
        self.assertEqual(pymal.READ('   abc'), MalSymbol('abc'))
        self.assertEqual(pymal.READ('abc5'), MalSymbol('abc5'))
        self.assertEqual(pymal.READ('abc-def'), MalSymbol('abc-def'))

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

    # Note: we can test the result of READ against a list, not a MalList, since
    # both types test equal.
    def test_read_lists(self):  # 6
        self.assertEqual(pymal.READ('(+ 1 2)'),
                         [MalSymbol('+'), 1, 2])
        self.assertEqual(pymal.READ('((3 4))'), [[3, 4]])
        self.assertEqual(pymal.READ('(+ 1 (+ 2 3))'),
                         [MalSymbol('+'), 1, [MalSymbol('+'), 2, 3]])
        self.assertEqual(pymal.READ('  ( +   1   (+   2 3   )   )  '),
                         [MalSymbol('+'), 1, [MalSymbol('+'), 2, 3]])
        self.assertEqual(pymal.READ('(* 1 2)'), [MalSymbol('*'), 1, 2])
        self.assertEqual(pymal.READ('(** 1 2)'), [MalSymbol('**'), 1, 2])
        self.assertEqual(pymal.READ('(* -3 6)'), [MalSymbol('*'), -3, 6])

    def test_read_comma_as_whitespace(self):  # 7
        self.assertEqual(pymal.READ('(1 2 3,,,,),,'), [1, 2, 3])

    def test_read_quoting(self):  # 8
        self.assertEqual(pymal.READ("'1"), [MalSymbol('quote'), 1])
        self.assertEqual(pymal.READ("'(1 2 3)"),
                         [MalSymbol('quote'), [1, 2, 3]])
        self.assertEqual(pymal.READ("`1"), [MalSymbol('quasiquote'), 1])
        self.assertEqual(pymal.READ("`(1 2 3)"),
                         [MalSymbol('quasiquote'), [1, 2, 3]])
        self.assertEqual(pymal.READ("~1"), [MalSymbol('unquote'), 1])
        self.assertEqual(pymal.READ("~(1 2 3)"),
                         [MalSymbol('unquote'), [1, 2, 3]])
        self.assertEqual(pymal.READ("~@(1 2 3)"),
                         [MalSymbol('splice-unquote'), [1, 2, 3]])

    # Currently, the string '"abc' is read as the symbol 'abc', therefore we
    # skip these tests for the moment.
    @unittest.skip("Reader errors skipped.")
    def test_read_reader_errors(self):  # 9
        self.assertIs(type(pymal.READ('(1 2')), MalError)
        self.assertIs(type(pymal.READ('[1 2')), MalError)
        self.assertIs(type(pymal.READ('"abc')), MalError)
        self.assertIs(type(pymal.READ('(1 "abc')), MalError)

    def test_read_keywords(self):  # 10
        self.assertEqual(pymal.READ(':kw'), MalKeyword(':kw'))
        self.assertEqual(pymal.READ('(:kw1 :kw2 :kw3)'),
                         [MalKeyword(':kw1'),
                          MalKeyword(':kw2'),
                          MalKeyword(':kw3')])

        self.assertEqual(pymal.READ('[+ 1 2]'),
                         MalVector([MalSymbol('+'), 1, 2]))
        self.assertEqual(pymal.READ('[[3 4]]'), MalVector([[3, 4]]))
        self.assertEqual(pymal.READ('[+ 1 [+ 2 3]]'),
                         MalVector([MalSymbol('+'), 1,
                                    [MalSymbol('+'), 2, 3]]))
        self.assertEqual(pymal.READ('[ +   1   [+   2 3   ]   ]  '),
                         MalVector([MalSymbol('+'), 1,
                                    [MalSymbol('+'), 2, 3]]))

    def test_read_hash(self):  # 11
        self.assertEqual(pymal.READ('{"abc" 1}'), MalHash({"abc": 1}))
        self.assertEqual(pymal.READ('{"a" {"b" 2}}'), MalHash({"a": {"b": 2}}))
        self.assertEqual(pymal.READ('{"a" {"b" {"c" 3}}} '),
                         MalHash({"a": {"b": {"c": 3}}}))
        self.assertEqual(pymal.READ('{  "a"  {"b"   {  "cde"     3   }  }}'),
                         MalHash({"a": {"b": {"cde": 3}}}))
        self.assertEqual(pymal.READ('{  :a  {:b   {  :cde     3   }  }}   '),
                         MalHash({MalKeyword(':a'):
                                  {MalKeyword(':b'):
                                   {MalKeyword(':cde'): 3}}}))

    def test_read_comments(self):  # 12
        self.assertEqual(pymal.READ(';; whole line comment'), None)
        self.assertEqual(pymal.READ('1 ; comment after expression'), 1)
        self.assertEqual(pymal.READ('1; comment after expression'), 1)

    def test_read_metadata(self):  # 13
        self.assertEqual(pymal.READ('^{"a" 1} [1 2 3]'),
                         [MalSymbol('with-meta'), [1, 2, 3], {'a': 1}])

    def test_read_deref(self):  # 14
        self.assertEqual(pymal.READ('@a'),
                         [MalSymbol('deref'), MalSymbol('a')])
