import pymal


class EvalAssert():
    def assertEval(self, ast, env, expected):
        res = pymal.rep(ast, env)
        if res != expected:
            raise AssertionError("eval failed: expected '{}', got '{}'".
                                 format(res, expected))
