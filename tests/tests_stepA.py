import unittest
from io import StringIO
from contextlib import redirect_stdout


import pymal
from mal_types import *
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStepA(unittest.TestCase, EvalAssert):
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
        # Set up *host-language*
        self.env.set("*host-language*", "Python3")

    @unittest.skip("Skip 'readline' test.")
    def test_readline(self):  # 86
        f = StringIO()
        with redirect_stdout(f):
            res = pymal.rep('(readline "mal-user> ")', self.env)
        self.assertEqual(res, r'\"hello\"')
        self.assertEqual(f.getvalue(), '"hello"')

    def test_host_language(self):  # 87
        self.assertEval('(= "Python3" *host-language*)', self.env, 'true')

    def test_meta_data_on_functions(self):  # 88
        self.assertEval('(meta (fn* (a) a))', self.env, 'nil')
        self.assertEval('(meta (with-meta (fn* (a) a) {"b" 1}))',
                        self.env, '{"b" 1}')
        self.assertEval('(meta (with-meta (fn* (a) a) "abc"))',
                        self.env, '"abc"')
        pymal.rep('(def! l-wm (with-meta (fn* (a) a) {"b" 2}))', self.env)
        self.assertEval('(meta l-wm)', self.env, '{"b" 2}')
        self.assertEval('(meta (with-meta l-wm {"new_meta" 123}))',
                        self.env, '{"new_meta" 123}')
        self.assertEval('(meta l-wm)', self.env, '{"b" 2}')
        pymal.rep('(def! f-wm (with-meta (fn* [a] (+ 1 a)) {"abc" 1}))',
                  self.env)
        self.assertEval('(meta f-wm)', self.env, '{"abc" 1}')
        self.assertEval('(meta (with-meta f-wm {"new_meta" 123}))',
                        self.env, '{"new_meta" 123}')
        self.assertEval('(meta f-wm)', self.env, '{"abc" 1}')
        pymal.rep('(def! f-wm2 ^{"abc" 1} (fn* [a] (+ 1 a)))', self.env)
        self.assertEval('(meta f-wm2)', self.env, '{"abc" 1}')
        # Meta of native functions should return nil (not fail)
        self.assertEval('(meta +)', self.env, 'nil')

    def test_closures_with_metadata(self):  # 89
        pymal.rep('(def! gen-plusX (fn* (x)'
                  '  (with-meta (fn* (b) (+ x b)) {"meta" 1})))', self.env)
        pymal.rep('(def! plus7 (gen-plusX 7))', self.env)
        pymal.rep('(def! plus8 (gen-plusX 8))', self.env)
        self.assertEval('(plus7 8)', self.env, '15')
        self.assertEval('(meta plus7)', self.env, '{"meta" 1}')
        self.assertEval('(meta plus8)', self.env, '{"meta" 1}')
        self.assertEval('(meta (with-meta plus7 {"meta" 2}))',
                        self.env, '{"meta" 2}')
        self.assertEval('(meta plus8)', self.env, '{"meta" 1}')

    def test_hash_map_evaluation_and_atoms(self):  # 90
        pymal.rep('(def! e (atom {"+" +}))', self.env)
        pymal.rep('(swap! e assoc "-" -)', self.env)
        self.assertEval('( (get @e "+") 7 8)', self.env, '15')
        self.assertEval('( (get @e "-") 11 8)', self.env, '3')
        pymal.rep('(swap! e assoc "foo" (list))', self.env)
        self.assertEval('(get @e "foo")', self.env, '()')
        pymal.rep('(swap! e assoc "bar" \'(1 2 3))', self.env)
        self.assertEval('(get @e "bar")', self.env, '(1 2 3)')

    def test_stringp(self):  # 91
        self.assertEval('(string? "")', self.env, 'true')
        self.assertEval('(string? \'abc)', self.env, 'false')
        self.assertEval('(string? "abc")', self.env, 'true')
        self.assertEval('(string? :abc)', self.env, 'false')
        self.assertEval('(string? (keyword "abc"))', self.env, 'false')
        self.assertEval('(string? 234)', self.env, 'false')
        self.assertEval('(string? nil)', self.env, 'false')

    def test_conj(self):  # 92
        self.assertEval('(conj (list) 1)', self.env, '(1)')
        self.assertEval('(conj (list 1) 2)', self.env, '(2 1)')
        self.assertEval('(conj (list 2 3) 4)', self.env, '(4 2 3)')
        self.assertEval('(conj (list 2 3) 4 5 6)', self.env, '(6 5 4 2 3)')
        self.assertEval('(conj (list 1) (list 2 3))', self.env, '((2 3) 1)')

        self.assertEval('(conj [] 1)', self.env, '[1]')
        self.assertEval('(conj [1] 2)', self.env, '[1 2]')
        self.assertEval('(conj [2 3] 4)', self.env, '[2 3 4]')
        self.assertEval('(conj [2 3] 4 5 6)', self.env, '[2 3 4 5 6]')
        self.assertEval('(conj [1] [2 3])', self.env, '[1 [2 3]]')

    def test_seq(self):  # 93
        self.assertEval('(seq "abc")', self.env, '("a" "b" "c")')
        self.assertEval('(apply str (seq "this is a test"))',
                        self.env, '"this is a test"')
        self.assertEval('(seq \'(2 3 4))', self.env, '(2 3 4)')
        self.assertEval('(seq [2 3 4])', self.env, '(2 3 4)')

        self.assertEval('(seq "")', self.env, 'nil')
        self.assertEval('(seq \'())', self.env, 'nil')
        self.assertEval('(seq [])', self.env, 'nil')
        self.assertEval('(seq nil)', self.env, 'nil')

    def test_metadata_on_collections(self):  # 94
        self.assertEval('(meta [1 2 3])', self.env, 'nil')
        self.assertEval('(with-meta [1 2 3] {"a" 1})', self.env, '[1 2 3]')
        self.assertEval('(meta (with-meta [1 2 3] {"a" 1}))',
                        self.env, '{"a" 1}')
        self.assertEval('(vector? (with-meta [1 2 3] {"a" 1}))',
                        self.env, 'true')
        self.assertEval('(meta (with-meta [1 2 3] "abc"))', self.env, '"abc"')
        self.assertEval('(meta (with-meta (list 1 2 3) {"a" 1}))',
                        self.env, '{"a" 1}')
        self.assertEval('(list? (with-meta (list 1 2 3) {"a" 1}))',
                        self.env, 'true')
        self.assertEval('(meta (with-meta {"abc" 123} {"a" 1}))',
                        self.env, '{"a" 1}')
        self.assertEval('(map? (with-meta {"abc" 123} {"a" 1}))',
                        self.env, 'true')

        self.assertEval('(def! l-wm (with-meta [4 5 6] {"b" 2}))',
                        self.env, '[4 5 6]')
        self.assertEval('(meta l-wm)', self.env, '{"b" 2}')
        self.assertEval('(meta (with-meta l-wm {"new_meta" 123}))',
                        self.env, '{"new_meta" 123}')
        self.assertEval('(meta l-wm)', self.env, '{"b" 2}')

    def test_metadata_on_atoms(self):  # 95
        self.assertEval('(meta (with-meta (atom 7) {"a" 1}))',
                        self.env, '{"a" 1}')

    def test_metadata_on_builtins(self):  # 96
        self.assertEval('(meta +)', self.env, 'nil')
        pymal.rep('(def! f-wm3 ^{"def" 2} +)', self.env)
        self.assertEval('(meta f-wm3)', self.env, '{"def" 2}')
        self.assertEval('(meta +)', self.env, 'nil')

    def test_gensym_and_clean_or(self):  # 97
        self.assertEval('(= (gensym) (gensym))', self.env, 'false')
        self.assertEval('(let* [or_FIXME 23] (or false (+ or_FIXME 100)))',
                        self.env, '123')

    def test_time_ms(self):  # 98
        pymal.rep('(def! start-time (time-ms))', self.env)
        self.assertEval('(> start-time 0)', self.env, 'true')
        self.assertEval('(let* [sumdown (fn* (N)'
                        '                 (if (> N 0)'
                        '                   (+ N (sumdown (- N 1)))'
                        '                   0))]'
                        '  (sumdown 10)) ; Waste some time',
                        self.env, '55')
        self.assertEval('(> (time-ms) start-time)', self.env, 'true')
