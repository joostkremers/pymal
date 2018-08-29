#!/usr/bin/env python3

# System imports
import readline  # so input() uses editable input
import sys

# Local imports
import reader
import printer
import mal_types as mal
import mal_env as menv
import core

repl_env = None


def READ(line):
    return reader.read_str(line)


def EVAL(ast, env):
    while True:
        if ast is None:  # comments
            return None
        if type(ast) is mal.Error:
            return ast
        elif type(ast) is not mal.List:
            return eval_ast(ast, env)
        else:  # if ast is a list
            if len(ast) == 0:  # if ast is the empty list, just return it
                return ast

            # perform macro expansion
            ast = macroexpand(ast, env)
            if type(ast) is not mal.List:
                return eval_ast(ast, env)

            # apply
            if type(ast[0]) is mal.Symbol:
                symbol = ast[0].name
                # Special forms
                if symbol == "def!":
                    return mal_def(env, ast[1:])
                elif symbol == "defmacro!":
                    return mal_defmacro(env, ast[1:])
                elif symbol == "try*":
                    catch = ast[2]
                    if not (catch[0].name == "catch*"):
                        return mal.Error("TryError",
                                         "Failing 'catch*' clause")

                    A = EVAL(ast[1], env)
                    if type(A) is mal.Error:
                        # The error is wrapped in a HandledError instance, so
                        # that evaluation is not halted.
                        A = mal.HandledError(A)
                        B = catch[1]
                        C = catch[2]
                        env = menv.mal.Env(outer=env, binds=[B], exprs=[A])
                        ast = C
                        continue
                    else:
                        return A
                elif symbol == "let*":
                    ast, env = mal_let(env, ast[1], ast[2])
                    continue
                elif symbol == "do":
                    evalled = eval_ast(mal.List(ast[1:-1]), env)
                    if type(evalled) is mal.Error:
                        return evalled
                    ast = ast[-1]
                    continue
                elif symbol == "if":
                    ast = mal_if(env, ast[1:])
                    continue
                elif symbol == "fn*":
                    return mal_fn(env, ast[1], ast[2])
                elif symbol == "quote":
                    return ast[1]
                elif symbol == "quasiquote":
                    ast = mal_quasiquote(ast[1])
                    continue
                elif symbol == "macroexpand":
                    return macroexpand(ast[1], env)

        # If the list does not start with a symbol or if the symbol is not a
        # special form, we evaluate and apply:
        evalled = eval_ast(ast, env)
        if type(evalled) is mal.Error:
            return evalled
        elif type(evalled[0]) is mal.Builtin:
            return evalled[0].fn(*evalled[1:])
        elif type(evalled[0]) is mal.Function:
            ast = evalled[0].ast
            env = menv.mal.Env(outer=evalled[0].env,
                               binds=evalled[0].params,
                               exprs=evalled[1:])
            continue
        else:
            return mal.Error("ApplyError",
                             "'{}' is not callable".format(evalled[0]))


# Special forms
def mal_def(environment, ast):
    if len(ast) != 2:
        return mal.Error("ArgError",
                         "'def!' requires 2 arguments, "
                         "received {}".format(len(ast)))
    symbol = ast[0]
    value = ast[1]
    evalled = EVAL(value, environment)
    if type(evalled) is not mal.Error:
        environment.set(symbol.name, evalled)
    return evalled


def mal_defmacro(environment, ast):
    if len(ast) != 2:
        return mal.Error("ArgError",
                         "'defmacro!' requires 2 arguments, "
                         "received {}".format(len(ast)))
    symbol = ast[0]
    value = ast[1]
    evalled = EVAL(value, environment)
    if type(evalled) is mal.Function:
        evalled.is_macro = True
    if type(evalled) is not mal.Error:
        environment.set(symbol.name, evalled)
    return evalled


def mal_let(environment, bindings, body):
    if not isinstance(bindings, (mal.List, mal.Vector)):
        return (mal.Error("LetError", "Invalid bind form"), None)
    if (len(bindings) % 2 != 0):
        return (mal.Error("LetError", "Insufficient bind forms"), None)

    new_env = menv.mal.Env(outer=environment)
    for i in range(0, len(bindings), 2):
        if type(bindings[i]) is not mal.Symbol:
            return (mal.Error("LetError", "Attempt to bind to non-symbol"),
                    None)

        evalled = EVAL(bindings[i + 1], new_env)
        if type(evalled) is mal.Error:
            return (evalled, None)

        new_env.set(bindings[i].name, evalled)

    return (body, new_env)


def mal_if(environment, args):
    if len(args) < 2:
        return mal.Error("ArgError",
                         "'if' requires 2-3 arguments, "
                         "received {}".format(len(args)))

    condition = EVAL(args[0], environment)
    if type(condition) is mal.Error:
        return condition
    if not (condition == mal.NIL or condition == mal.Boolean(False)):
        return args[1]
    else:
        if len(args) == 3:
            return args[2]
        else:
            return mal.NIL


def mal_fn(environment, syms, body):
    if '&' in syms:
        if syms.index('&') != len(syms) - 2:
            return mal.Error("BindsError", "Illegal binds list")

    def mal_closure(*params):
        new_env = menv.mal.Env(outer=environment, binds=syms, exprs=params)
        return EVAL(body, new_env)

    return mal.Function(mal_closure, syms, body, environment)


def is_pair(arg):
    """Return True if ARG is a non-empty list or vector."""

    if isinstance(arg, list) and len(arg) > 0:
        return True
    else:
        return False


def mal_quasiquote(ast):
    # not a list (or empty list)
    if not is_pair(ast):
        return mal.List((mal.Symbol("quote"), ast))

    # unquote
    elif type(ast[0]) is mal.Symbol and ast[0].name == "unquote":
        return ast[1]

    # splice-unquote
    elif (is_pair(ast[0]) and
          type(ast[0][0]) is mal.Symbol and
          ast[0][0].name == "splice-unquote"):
        first = mal.Symbol("concat")
        second = ast[0][1]
        rest = mal_quasiquote(mal.List(ast[1:]))
        return mal.List((first, second, rest))

    # otherwise
    else:
        first = mal.Symbol("cons")
        second = mal_quasiquote(ast[0])
        rest = mal_quasiquote(mal.List(ast[1:]))
        return mal.List((first, second, rest))


def is_macro_call(ast, env):
    if type(ast) is not mal.List:
        return False
    if type(ast[0]) is not mal.Symbol:
        return False

    fn = env.get(ast[0].name)
    if type(fn) is mal.Function:
        return fn.is_macro
    else:
        return False


def macroexpand(ast, env):
    while is_macro_call(ast, env):
        fn = env.get(ast[0].name)
        ast = fn.fn(*ast[1:])
    return ast


def PRINT(data):
    return printer.pr_str(data, print_readably=True)


def eval_ast(ast, env):
    if type(ast) is mal.Symbol:
        return env.get(ast.name)

    elif type(ast) is mal.List:
        res = []
        for elem in ast:
            val = EVAL(elem, env)
            if type(val) is mal.Error:
                return val
            res.append(val)
        return mal.List(res)

    elif type(ast) is mal.Vector:
        res = []
        for elem in ast:
            val = EVAL(elem, env)
            if type(val) is mal.Error:
                return val
            res.append(val)
        return mal.Vector(res)

    elif type(ast) is mal.Hash:
        res = {}
        for key, val in ast.items():
            newval = EVAL(val, env)
            if type(newval) is mal.Error:
                return newval
            res[key] = newval
        return mal.Hash(res)

    else:
        return ast


# These builtins are defined here and not in core.py because they call EVAL:
def mal_eval(ast):
    global repl_env
    return EVAL(ast, repl_env)


def mal_swap(atom, fn, *args):
    global repl_env

    if type(atom) is not mal.Atom:
        return mal.Error("TypeError",
                         "Expected atom, received {}".format(type(atom)))

    evalled = fn.fn(atom.value, *args)
    atom.set(evalled)
    return evalled


def rep(line, env):
    ast = READ(line)
    result = EVAL(ast, env)
    return PRINT(result)


def Mal(args=[]):
    global repl_env
    repl_env = menv.mal.Env()

    for sym in core.ns:
        repl_env.set(sym, core.ns[sym])

    # Add eval and swap! to repl_env:
    repl_env.set("eval", mal.Builtin(mal_eval))
    repl_env.set("swap!", mal.Builtin(mal_swap))

    # Add the command line arguments to repl_env:
    repl_env.set("*ARGV*", mal.List(args[1:]))

    # Add *host-language*:
    repl_env.set("*host-language*", "Python3")

    # Add a 'load-file' function:
    rep("(def! load-file (fn* (f)"
        "  (eval (read-string (str \"(do \" (slurp f) \")\")))))", repl_env)

    # Load Mal core
    rep('(load-file "prelude.mal")', repl_env)

    if len(args) >= 1:
        rep('(load-file "{}")'.format(args[0]), repl_env)
        return

    rep("(println (str \"Mal [\" *host-language* \"]\"))", repl_env)

    while True:
        try:
            line = input("user> ")
        except EOFError:
            print("\n\nBye")
            break
        if line == "quit":
            print("\n\nBye")
            break
        result = rep(line, repl_env)
        print(result)


if __name__ == '__main__':
    Mal(sys.argv[1:])
