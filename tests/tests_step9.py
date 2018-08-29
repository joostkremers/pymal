import unittest
from io import StringIO
from contextlib import redirect_stdout


import pymal
import mal_types as mal
import core
import mal_env as menv
from eval_assert import EvalAssert


class TestStep9(unittest.TestCase, EvalAssert):
    def setUp(self):
        self.env = menv.MalEnv()
        for sym in core.ns:
            self.env.set(sym, core.ns[sym])

        # Add 'eval' and 'swap!' functions
        self.env.set("eval", mal.Builtin(pymal.mal_eval))
        self.env.set("swap!", mal.Builtin(pymal.mal_swap))
        # set repl_env for 'eval'
        pymal.repl_env = self.env

        # Add 'load-file' and use it to load the prelude
        pymal.rep('(def! load-file (fn* (f)'
                  '  (eval'
                  '    (read-string (str "(do " (slurp f) ")")))))',
                  self.env)
        pymal.rep('(load-file "prelude.mal")', self.env)

    def test_try_catch(self):  # 69
        self.assertEval('(try* 123 (catch* e 456))', self.env, '123')

        f = StringIO()
        with redirect_stdout(f):
            res = pymal.rep('(try* (abc 1 2)'
                            '  (catch* exc (prn "exc is:" exc)))', self.env)
        self.assertEqual(res, 'nil')
        self.assertEqual(f.getvalue(),
                         '"exc is:" Symbol value is void: \'abc\'\n')

        g = StringIO()
        with redirect_stdout(g):
            res = pymal.rep('(try* (throw (list 1 2 3))'
                            '  (catch* exc (do (prn "err:" exc) 7)))',
                            self.env)
        self.assertEqual(res, '7')
        self.assertEqual(g.getvalue(),
                         '"err:" (1 2 3)\n')

        h = StringIO()
        with redirect_stdout(h):
            res = pymal.rep('(try* (throw "my exception")'
                            '  (catch* exc (do (prn "err:" exc) 7)))',
                            self.env)
        self.assertEqual(res, '7')
        self.assertEqual(h.getvalue(),
                         '"err:" my exception\n')

    def test_throw_is_function(self):  # 70
        self.assertEval('(try* (map throw (list 7)) (catch* exc exc))',
                        self.env, '7')

    def test_builin_functions(self):  # 71
        self.assertEval("(symbol? 'abc)", self.env, 'true')
        self.assertEval('(symbol? "abc")', self.env, 'false')

        self.assertEval('(nil? nil)', self.env, 'true')
        self.assertEval('(nil? true)', self.env, 'false')

        self.assertEval('(true? true)', self.env, 'true')
        self.assertEval('(true? false)', self.env, 'false')
        self.assertEval('(true? true?)', self.env, 'false')

        self.assertEval('(false? false)', self.env, 'true')
        self.assertEval('(false? true)', self.env, 'false')

    def test_apply_with_core_functions(self):  # 72
        self.assertEval('(apply + (list 2 3))', self.env, '5')
        self.assertEval('(apply + 4 (list 5))', self.env, '9')

        f = StringIO()
        with redirect_stdout(f):
            res = pymal.rep('(apply prn (list 1 2 "3" (list)))', self.env)
        self.assertEqual(res, 'nil')
        self.assertEqual(f.getvalue(), '1 2 "3" ()\n')

        g = StringIO()
        with redirect_stdout(g):
            res = pymal.rep('(apply prn 1 2 (list "3" (list)))', self.env)
        self.assertEqual(res, 'nil')
        self.assertEqual(g.getvalue(), '1 2 "3" ()\n')

    def test_apply_with_user_functions(self):  # 73
        self.assertEval('(apply (fn* (a b) (+ a b)) (list 2 3))',
                        self.env, '5')
        self.assertEval('(apply (fn* (a b) (+ a b)) 4 (list 5))',
                        self.env, '9')

    def test_map_function(self):  # 74
        pymal.rep('(def! nums (list 1 2 3))', self.env)
        pymal.rep('(def! double (fn* (a) (* 2 a)))', self.env)

        self.assertEval('(double 3)', self.env, '6')
        self.assertEval('(map double nums) ', self.env, '(2 4 6)')
        self.assertEval('(map (fn* (x)'
                        '       (symbol? x))'
                        '     (list 1 (symbol "two") "three"))',
                        self.env, '(false true false)')

    def test_symbol_and_keyword_functions(self):  # 75
        self.assertEval('(symbol? :abc)', self.env, 'false')
        self.assertEval("(symbol? 'abc)", self.env, 'true')
        self.assertEval('(symbol? "abc")', self.env, 'false')
        self.assertEval('(symbol? (symbol "abc"))', self.env, 'true')

        self.assertEval('(keyword? :abc)', self.env, 'true')
        self.assertEval("(keyword? 'abc)", self.env, 'false')
        self.assertEval('(keyword? "abc")', self.env, 'false')
        self.assertEval('(keyword? "")', self.env, 'false')
        self.assertEval('(keyword? (keyword "abc"))', self.env, 'true')

        self.assertEval('(symbol "abc")', self.env, 'abc')
        self.assertEval('(keyword :abc)', self.env, ':abc')
        self.assertEval('(keyword "abc")', self.env, ':abc')

    def test_sequentialp(self):  # 76
        self.assertEval('(sequential? (list 1 2 3))', self.env, 'true')
        self.assertEval('(sequential? [15])', self.env, 'true')
        self.assertEval('(sequential? sequential?)', self.env, 'false')
        self.assertEval('(sequential? nil)', self.env, 'false')
        self.assertEval('(sequential? "abc")', self.env, 'false')

    def test_apply_core_functions_with_vector(self):  # 77
        self.assertEval('(apply + 4 [5])', self.env, '9')

        f = StringIO()
        with redirect_stdout(f):
            res = pymal.rep('(apply prn 1 2 ["3" 4])', self.env)
        self.assertEqual(res, 'nil')
        self.assertEqual(f.getvalue(), '1 2 "3" 4\n')

    def test_apply_user_functions_with_vector(self):  # 78
        self.assertEval('(apply (fn* (a b) (+ a b)) [2 3])', self.env, '5')
        self.assertEval('(apply (fn* (a b) (+ a b)) 4 [5])', self.env, '9')

    def test_map_with_vector(self):  # 79
        self.assertEval('(map (fn* (a) (* 2 a)) [1 2 3])', self.env, '(2 4 6)')

    def test_vector_functions(self):  # 80
        self.assertEval('(vector? [10 11])', self.env, 'true')
        self.assertEval("(vector? '(12 13))", self.env, 'false')
        self.assertEval('(vector 3 4 5)', self.env, '[3 4 5]')

        self.assertEval('(map? {})', self.env, 'true')
        self.assertEval("(map? '())", self.env, 'false')
        self.assertEval('(map? [])', self.env, 'false')
        self.assertEval("(map? 'abc)", self.env, 'false')
        self.assertEval('(map? :abc)', self.env, 'false')

    def test_hash_maps(self):  # 81
        self.assertEval('(hash-map "a" 1)', self.env, '{"a" 1}')
        self.assertEval('{"a" 1}', self.env, '{"a" 1}')
        self.assertEval('(assoc {} "a" 1)', self.env, '{"a" 1}')
        self.assertEval('(get (assoc (assoc {"a" 1 } "b" 2) "c" 3) "a")',
                        self.env, '1')
        self.assertEval('(def! hm1 (hash-map))', self.env, '{}')
        self.assertEval('(map? hm1)', self.env, 'true')
        self.assertEval('(map? 1)', self.env, 'false')
        self.assertEval('(map? "abc")', self.env, 'false')
        self.assertEval('(get nil "a")', self.env, 'nil')
        self.assertEval('(get hm1 "a")', self.env, 'nil')
        self.assertEval('(contains? hm1 "a")', self.env, 'false')
        self.assertEval('(def! hm2 (assoc hm1 "a" 1))', self.env, '{"a" 1}')
        self.assertEval('(get hm1 "a")', self.env, 'nil')
        self.assertEval('(contains? hm1 "a")', self.env, 'false')
        self.assertEval('(get hm2 "a")', self.env, '1')
        self.assertEval('(contains? hm2 "a")', self.env, 'true')
        # TODO: fix. Clojure returns nil but this breaks mal impl
        self.assertEval('(keys hm1)', self.env, '()')
        self.assertEval('(keys hm2)', self.env, '("a")')
        # TODO: fix. Clojure returns nil but this breaks mal impl
        self.assertEval('(vals hm1)', self.env, '()')
        self.assertEval('(vals hm2)', self.env, '(1)')
        self.assertEval('(count (keys (assoc hm2 "b" 2 "c" 3)))',
                        self.env, '3')
        pymal.rep('(def! hm3 (assoc hm2 "b" 2))', self.env)
        self.assertEval('(count (keys hm3))', self.env, '2')
        self.assertEval('(count (vals hm3))', self.env, '2')
        self.assertEval('(dissoc hm3 "a")', self.env, '{"b" 2}')
        self.assertEval('(dissoc hm3 "a" "b")', self.env, '{}')
        self.assertEval('(dissoc hm3 "a" "b" "c")', self.env, '{}')
        self.assertEval('(count (keys hm3))', self.env, '2')

    def test_keywords_as_hash_keys(self):  # 82
        self.assertEval('(get {:abc 123} :abc)', self.env, '123')
        self.assertEval('(contains? {:abc 123} :abc)', self.env, 'true')
        self.assertEval('(contains? {:abcd 123} :abc)', self.env, 'false')
        self.assertEval('(assoc {} :bcd 234)', self.env, '{:bcd 234}')
        self.assertEval('(dissoc {:cde 345 :fgh 456} :cde)',
                        self.env, '{:fgh 456}')
        self.assertEval('(keyword? (nth (keys {:abc 123 :def 456}) 0))',
                        self.env, 'true')
        self.assertEval('(keyword? (nth (keys {":abc" 123 ":def" 456}) 0))',
                        self.env, 'false')
        self.assertEval('(keyword? (nth (vals {"a" :abc "b" :def}) 0))',
                        self.env, 'true')

    def test_nil_as_hash_value(self):  # 83
        self.assertEval('(contains? {:abc nil} :abc)', self.env, 'true')
        self.assertEval('(assoc {} :bcd nil)', self.env, '{:bcd nil}')
        self.assertEval('(dissoc {:cde nil :fgh 456} :cde)',
                        self.env, '{:fgh 456}')

    def test_equality_of_hash_maps(self):  # 84
        self.assertEval('(= {} {})', self.env, 'true')
        self.assertEval('(= {:a 11 :b 22} (hash-map :b 22 :a 11))',
                        self.env, 'true')
        self.assertEval('(= {:a 11 :b [22 33]} (hash-map :b [22 33] :a 11))',
                        self.env, 'true')
        self.assertEval('(= {:a 11 :b {:c 33}} (hash-map :b {:c 33} :a 11))',
                        self.env, 'true')
        self.assertEval('(= {:a 11 :b 22} (hash-map :b 23 :a 11))',
                        self.env, 'false')
        self.assertEval('(= {:a 11 :b 22} (hash-map :a 11))',
                        self.env, 'false')
        self.assertEval('(= {:a [11 22]} {:a (list 11 22)})',
                        self.env, 'true')
        self.assertEval('(= {:a 11 :b 22} (list :a 11 :b 22))',
                        self.env, 'false')
        self.assertEval('(= {} [])', self.env, 'false')
        self.assertEval('(= [] {})', self.env, 'false')

    def test_additional_str_and_pr_str(self):  # 85
        self.assertEval('(str "A" {:abc "val"} "Z")',
                        self.env, '"A{:abc val}Z"')

        self.assertEval('(str true "." false "." nil "." :keyw "." \'symb)',
                        self.env, '"true.false.nil.:keyw.symb"')

        self.assertEval('(pr-str "A" {:abc "val"} "Z")',
                        self.env, r'"\"A\" {:abc \"val\"} \"Z\""')

        self.assertEval('(pr-str true "." false "." nil "." :keyw "." \'symb)',
                        self.env,
                        r'"true \".\" false \".\" nil \".\" :keyw \".\" symb"')

        pymal.rep('(def! s (str {:abc "val1" :def "val2"}))', self.env)
        self.assertEval('(or (= s "{:abc val1 :def val2}")'
                        '    (= s "{:def val2 :abc val1}"))', self.env, 'true')

        pymal.rep('(def! p (pr-str {:abc "val1" :def "val2"}))', self.env)
        self.assertEval(r'(or (= p "{:abc \"val1\" :def \"val2\"}")'
                        r'    (= p "{:def \"val2\" :abc \"val1\"}"))',
                        self.env, 'true')
