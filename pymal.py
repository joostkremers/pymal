#!/usr/bin/env python3

# System imports
import readline  # so input() uses editable input
import sys

# Local imports
import reader
import printer
from mal_types import *
import mal_env as menv
import core

repl_env = None


def READ(line):
    return reader.read_str(line)


def EVAL(ast, env):
    while True:
        if type(ast) is MalError:
            return ast
        elif type(ast) is not list:
            return eval_ast(ast, env)
        else:  # if ast is a list
            if len(ast) == 0:  # if ast is the empty list, just return it
                return ast

            # perform macro expansion
            ast = macroexpand(ast, env)
            if type(ast) is not list:
                return eval_ast(ast, env)

            # apply
            if type(ast[0]) is MalSymbol:
                symbol = ast[0].name
                # Special forms
                if symbol == "def!":
                    return mal_def(env, ast[1:])
                elif symbol == "defmacro!":
                    return mal_defmacro(env, ast[1:])
                elif symbol == "try*":
                    catch = ast[2]
                    if not (catch[0].name == "catch*"):
                        return MalError("TryError",
                                        "Failing 'catch*' clause")

                    A = EVAL(ast[1], env)
                    if type(A) is MalError:
                        # The error is wrapped in a HandledError instance, so
                        # that evaluation is not halted.
                        A = MalHandledError(A)
                        B = catch[1]
                        C = catch[2]
                        env = menv.MalEnv(outer=env, binds=[B], exprs=[A])
                        ast = C
                        continue
                    else:
                        return A
                elif symbol == "let*":
                    ast, env = mal_let(env, ast[1], ast[2])
                    continue
                elif symbol == "do":
                    evalled = eval_ast(ast[1:-1], env)
                    if type(evalled) is MalError:
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
        if type(evalled) is MalError:
            return evalled
        elif type(evalled[0]) is MalBuiltin:
            return evalled[0].fn(*evalled[1:])
        elif type(evalled[0]) is MalFunction:
            ast = evalled[0].ast
            env = menv.MalEnv(outer=evalled[0].env,
                              binds=evalled[0].params,
                              exprs=evalled[1:])
            continue
        else:
            return MalError("ApplyError",
                            "'{}' is not callable".format(evalled[0]))


# Special forms
def mal_def(environment, ast):
    if len(ast) != 2:
        return MalError("ArgError",
                        "'def!' requires 2 arguments, "
                        "received {}".format(len(ast)))
    symbol = ast[0]
    value = ast[1]
    evalled = EVAL(value, environment)
    if type(evalled) is not MalError:
        environment.set(symbol.name, evalled)
    return evalled


def mal_defmacro(environment, ast):
    if len(ast) != 2:
        return MalError("ArgError",
                        "'defmacro!' requires 2 arguments, "
                        "received {}".format(len(ast)))
    symbol = ast[0]
    value = ast[1]
    evalled = EVAL(value, environment)
    if type(evalled) is MalFunction:
        evalled.is_macro = True
    if type(evalled) is not MalError:
        environment.set(symbol.name, evalled)
    return evalled


def mal_let(environment, bindings, body):
    if not isinstance(bindings, (list, MalVector)):
        return (MalError("LetError", "Invalid bind form"), None)
    if (len(bindings) % 2 != 0):
        return (MalError("LetError", "Insufficient bind forms"), None)

    new_env = menv.MalEnv(outer=environment)
    # Note: bindings may be a list or an MalVector.
    if type(bindings) is MalVector:
        bindings = bindings.value
    for i in range(0, len(bindings), 2):
        if type(bindings[i]) is not MalSymbol:
            return (MalError("LetError", "Attempt to bind to non-symbol"),
                    None)

        evalled = EVAL(bindings[i+1], new_env)
        if type(evalled) is MalError:
            return (evalled, None)

        new_env.set(bindings[i].name, evalled)

    return (body, new_env)


def mal_if(environment, args):
    if len(args) < 2:
        return MalError("ArgError",
                        "'if' requires 2-3 arguments, "
                        "received {}".format(len(args)))

    condition = EVAL(args[0], environment)
    if not (condition == MalNil() or condition == MalBoolean(False)):
        return args[1]
    else:
        if len(args) == 3:
            return args[2]
        else:
            return MalNil()


def mal_fn(environment, syms, body):
    if type(syms) is MalVector:
        syms = syms.value

    if '&' in syms:
        if syms.index('&') != len(syms) - 2:
            return MalError("BindsError", "Illegal binds list")

    def mal_closure(*params):
        new_env = menv.MalEnv(outer=environment, binds=syms, exprs=params)
        return EVAL(body, new_env)

    return MalFunction(mal_closure, syms, body, environment)


def is_pair(arg):
    """Return True if ARG is a non-empty list or vector."""

    if isinstance(arg, (list, MalVector)) and len(arg) > 0:
        return True
    else:
        return False


def mal_quasiquote(ast):
    # not a list (or empty list)
    if not is_pair(ast):
        return list((MalSymbol("quote"), ast))

    # unquote
    elif type(ast[0]) is MalSymbol and ast[0].name == "unquote":
        return ast[1]

    # splice-unquote
    elif (is_pair(ast[0]) and
          type(ast[0][0]) is MalSymbol and
          ast[0][0].name == "splice-unquote"):
        first = MalSymbol("concat")
        second = ast[0][1]
        rest = mal_quasiquote(ast[1:])
        return list((first, second, rest))

    # otherwise
    else:
        first = MalSymbol("cons")
        second = mal_quasiquote(ast[0])
        rest = mal_quasiquote(ast[1:])
        return list((first, second, rest))


def is_macro_call(ast, env):
    if type(ast) is not list:
        return False
    if type(ast[0]) is not MalSymbol:
        return False

    fn = env.get(ast[0].name)
    if type(fn) is MalFunction:
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
    if type(ast) is MalSymbol:
        return env.get(ast.name)

    elif type(ast) is list:
        return eval_list(ast, env)

    elif type(ast) is MalVector:
        return MalVector(eval_list(ast.value, env))

    elif type(ast) is dict:
        res = {}
        for key, val in ast.items():
            newval = EVAL(val, env)
            if type(newval) is MalError:
                return newval
            res[key] = newval
        return res

    else:
        return ast


def eval_list(ast, env):
    res = []
    for elem in ast:
        val = EVAL(elem, env)
        if type(val) is MalError:
            return val
        res.append(val)
    return res


# These builtins are defined here and not in core.py because they call EVAL:
def mal_eval(ast):
    global repl_env
    return EVAL(ast, repl_env)


def mal_swap(atom, fn, *args):
    global repl_env

    if type(atom) is not MalAtom:
        return MalError("TypeError",
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
    repl_env = menv.MalEnv()

    for sym in core.ns:
        repl_env.set(sym, core.ns[sym])

    # Add eval and swap! to repl_env:
    repl_env.set("eval", MalBuiltin(mal_eval))
    repl_env.set("swap!", MalBuiltin(mal_swap))

    # Add the command line arguments to repl_env:
    repl_env.set("*ARGV*", list(args[1:]))

    # Add *host-language*:
    repl_env.set("*host-language*", "Python3")

    # Add a language-defined 'not' function:
    rep("(def! not (fn* (a) (if a false true)))", repl_env)

    # Add a 'load-file' function:
    rep("(def! load-file (fn* (f)"
        "  (eval (read-string (str \"(do \" (slurp f) \")\")))))", repl_env)

    # Add gensym
    rep("(def! *gensym-counter* (atom 0))", repl_env)
    rep("(def! gensym (fn* []"
        "  (symbol (str \"G__\""
        "    (swap! *gensym-counter* (fn* [x] (+ 1 x)))))))", repl_env)

    # Add 'cond' and 'or'
    rep("(defmacro! cond (fn* (& xs)"
        "  (if (> (count xs) 0)"
        "       (list 'if (first xs)"
        "          (if (> (count xs) 1)"
        "               (nth xs 1)"
        "             (throw \"odd number of forms to cond\"))"
        "          (cons 'cond (rest (rest xs)))))))", repl_env)
    rep("(defmacro! or (fn* (& xs)"
        "  (if (empty? xs)"
        "      nil"
        "    (if (= 1 (count xs))"
        "        (first xs)"
        "      (let* (condvar (gensym))"
        "        `(let* (~condvar ~(first xs))"
        "           (if ~condvar"
        "               ~condvar"
        "             (or ~@(rest xs)))))))))", repl_env)

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
