import copy
import time
import numbers

import mal_types as mal
import printer
import reader


# Arithmetic functions
def mal_add(*args):
    """Sum numbers.

    If ARGS contains only one element, it is returned. If ARG is empty, the
    return value is 0.

    """
    try:
        res = sum(args)
    except TypeError:
        return mal.Error("ArgError", "'+': Wrong type argument")

    return res


def mal_substract(*args):
    """Substract numbers.

    If ARG contains just a single element, it is negated. If ARG is empty, the
    return value is 0.

    """
    if len(args) > 1:
        first = args[0]
        args = args[1:]
    else:
        first = 0

    try:
        for n in args:
            first -= n
    except TypeError:
        return mal.Error("ArgError", "'-': Wrong type argument")

    return first


def mal_multiply(*args):
    """Multiply numbers.

    If args contains only one element, it is returned. If ARG is empty, the
    return value is 1.

    """
    if len(args) > 1:
        first = args[0]
        args = args[1:]
    else:
        first = 1

    try:
        for n in args:
            first *= n
    except TypeError:
        return mal.Error("ArgError", "'*': Wrong type argument")

    return first


def mal_divide(*args):
    """Divide numbers.

    If ARGS contains zero or one element(s), the return value is 0.

    """
    if len(args) > 1:
        first = args[0]
        args = args[1:]
    else:
        first = 0

    try:
        for n in args:
            first //= n
    except ZeroDivisionError:
        return mal.Error("ArithmeticError", "Division by zero")
    except TypeError:
        return mal.Error("ArgError", "'/': Wrong type argument")

    return first


# comparison functions
def mal_equal(*args):
    first = args[0]
    for arg in args[1:]:
        if arg != first:
            return mal.Boolean(False)

    return mal.Boolean(True)


def mal_less(*args):
    for i in range(len(args) - 1):
        if not isinstance(args[i], numbers.Number):
            return mal.Error("ArgError",
                             "Wrong type argument: "
                             "expected number, got {}".format(type(args[i])))
        if not args[i] < args[i + 1]:
            return mal.Boolean(False)
    return mal.Boolean(True)


def mal_less_or_equal(*args):
    for i in range(len(args) - 1):
        if not isinstance(args[i], numbers.Number):
            return mal.Error("ArgError",
                             "'<=': Wrong type argument: "
                             "expected number, got {}".format(type(args[i])))
        if not args[i] <= args[i + 1]:
            return mal.Boolean(False)
    return mal.Boolean(True)


def mal_greater(*args):
    for i in range(len(args) - 1):
        if not isinstance(args[i], numbers.Number):
            return mal.Error("ArgError",
                             "'>': Wrong type argument: "
                             "expected number, got {}".format(type(args[i])))
        if not args[i] > args[i + 1]:
            return mal.Boolean(False)
    return mal.Boolean(True)


def mal_greater_or_equal(*args):
    for i in range(len(args) - 1):
        if not isinstance(args[i], numbers.Number):
            return mal.Error("ArgError",
                             "'>=': Wrong type argument: "
                             "expected number, got {}".format(type(args[i])))
        if not args[i] >= args[i + 1]:
            return mal.Boolean(False)
    return mal.Boolean(True)


# list / vector functions
def mal_cons(obj, lst):
    if not isinstance(lst, list):
        return mal.Error("ArgError", "'cons': Wrong type argument: "
                         "expected list or vector, got {}".format(type(lst)))
    return mal.List([obj] + lst)


def mal_concat(*args):
    res = []
    for arg in args:
        res.extend(arg)
    return mal.List(res)


def mal_conj(seq, *elems):
    """Add ELEMS to SEQ (a list or vector).

    If SEQ is a list, the elements in ELEMS are added to the front of the list
    in reverse order. If SEQ is a vector, the elements are added to the end.

    """
    if not isinstance(seq, (mal.List, mal.Vector)):
        return mal.Error("ArgError", "'conj': Wrong type argument:"
                         "expected list or vector, received {}".
                         format(type(seq)))

    if type(seq) is mal.List:
        return mal.List(list(elems[::-1]) + seq)

    if type(seq) is mal.Vector:
        return mal.Vector(seq[:] + mal.Vector(elems))


def mal_nth(arg, index):
    if not isinstance(arg, (mal.List, mal.Vector)):
        return mal.Error("ArgError", "'nth': Wrong type argument:"
                         "expected list or vector, received {}".
                         format(type(arg)))
    if index >= len(arg):
        return mal.Error("IndexError", "Index out of range")

    return arg[index]


def mal_first(arg):
    if not isinstance(arg, (mal.List, mal.Vector, mal.Nil)):
        return mal.Error("ArgError", "'nth': Wrong type argument:"
                         "expected list or vector, received {}".
                         format(type(arg)))

    if arg == mal.NIL or len(arg) == 0:
        return mal.NIL

    return arg[0]


def mal_rest(arg):
    if arg == mal.NIL:
        return mal.List([])
    elif isinstance(arg, (mal.List, mal.Vector)):
        return mal.List(arg[1:])
    else:
        return mal.Error("ArgError", "'nth': Wrong type argument:"
                         "expected list or vector, received {}".
                         format(type(arg)))


def mal_list(*args):
    return mal.List(args)


def mal_listp(arg):
    if type(arg) is mal.List:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_emptyp(arg):
    if not isinstance(arg, (mal.List, mal.Vector)):
        return mal.Error("ArgError",
                         "'empty?': Wrong type argument: "
                         "expected list or vector, got {}".format(type(arg)))
    if arg == []:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_count(arg):
    if arg == mal.NIL:
        return 0
    if not isinstance(arg, (mal.List, mal.Vector)):
        return mal.Error("ArgError",
                         "'count': Wrong type argument: "
                         "expected list or vector, got {}".format(type(arg)))
    return len(arg)


# printing functions
def mal_pr_str(*args):
    return " ".join([printer.pr_str(arg, True) for arg in args])


def mal_str(*args):
    return "".join([printer.pr_str(arg, False) for arg in args])


def mal_prn(*args):
    print(" ".join([printer.pr_str(arg, True) for arg in args]))
    return mal.NIL


def mal_println(*args):
    print(" ".join([printer.pr_str(arg, False) for arg in args]))
    return mal.NIL


# file functions
def mal_slurp(filename):
    try:
        f = open(filename, 'r')
        conts = f.read()
    except FileNotFoundError:
        return mal.Error("FileError", "File not found")
    return conts


# readline
def mal_readline(prompt):
    try:
        line = input(prompt)
    except EOFError:
        return mal.NIL
    return line


# atom functions
def mal_atom(object):
    return mal.Atom(object)


def mal_atomp(object):
    if type(object) is mal.Atom:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_deref(atom):
    if type(atom) is not mal.Atom:
        return mal.Error("TypeError",
                         "Expected atom, received {}".format(type(atom)))
    else:
        return atom.value


def mal_reset(atom, value):
    if type(atom) is not mal.Atom:
        return mal.Error("TypeError",
                         "Expected atom, received {}".format(type(atom)))
    else:
        atom.set(value)
        return value


# throw
def mal_throw(arg):
    return mal.Error("UserError", str(arg))


# functional functions
def mal_apply(fn, *args):
    if not isinstance(fn, (mal.Builtin, mal.Function)):
        return mal.Error("TypeError", "'apply': Expected function,"
                         " received {}".format(fn))

    lastarg = args[-1]
    if not isinstance(lastarg, (mal.List, mal.Vector)):
        return mal.Error("TypeError", "'apply': Expected list or vector,"
                         " received {}".format(args[-1]))

    allargs = list(args[:-1]) + lastarg

    return fn.fn(*allargs)


def mal_map(fn, lst):
    if not isinstance(fn, (mal.Builtin, mal.Function)):
        return mal.Error("TypeError", "'map': Expected function,"
                         " received {}".format(fn))

    if not isinstance(lst, (mal.List, mal.Vector)):
        return mal.Error("TypeError", "Expected list or vector,"
                         " received {}".format(lst))

    res = []
    for elem in lst:
        evalled = fn.fn(elem)
        if type(evalled) is mal.Error:
            return evalled
        res.append(evalled)

    return mal.List(res)


# type functions
def mal_symbol(arg):
    if type(arg) is not str:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected string, received {}".format(arg))
    return mal.Symbol(arg)


def mal_keyword(arg):
    if type(arg) is mal.Keyword:
        return arg
    if type(arg) is not str:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected string, received {}".format(type(arg)))
    return mal.Keyword(arg)


def mal_vector(*args):
    return mal.Vector(list(args))


def mal_seq(arg):
    """Turn ARG into a list.

    If ARG is nil or an empty list, vector or string, return nil. If ARG is a
    non-empty list, return it unchanged; if ARG is a non-empty vector, convert
    it to a list; if ARG is a non-empty string, return a list of characters.

    """
    if arg == mal.NIL:
        return arg

    if len(arg) == 0:
        return mal.NIL

    if type(arg) is mal.List:
        return arg

    if type(arg) is mal.Vector:
        return mal.List(arg)

    if type(arg) is str:
        return mal.List(arg)

    # if all fails, return an error
    return mal.Error("ArgError", "'seq': Wrong type argument: "
                     "expected sequence, received {}".format(type(arg)))


# type predicates
def mal_nilp(arg):
    if arg == mal.NIL:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_truep(arg):
    if arg == mal.Boolean(True):
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_falsep(arg):
    if arg == mal.Boolean(False):
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_symbolp(arg):
    if type(arg) is mal.Symbol:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_keywordp(arg):
    if type(arg) is mal.Keyword:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_vectorp(arg):
    if type(arg) is mal.Vector:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_mapp(arg):
    if type(arg) is mal.Hash:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_sequentialp(arg):
    if isinstance(arg, (mal.List, mal.Vector)):
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_stringp(arg):
    if type(arg) is str:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_typeof(arg):
    return type(arg)


# hash functions
def mal_hashmap(*args):
    return reader.create_hash(args)


def mal_assoc(hashmap, *args):
    if type(hashmap) is not mal.Hash:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected hash, received {}".format(type(hashmap)))
    orig = hashmap.copy()

    new = reader.create_hash(list(args))
    if type(new) is mal.Error:
        return new

    orig.update(new)
    return mal.Hash(orig)


def mal_dissoc(hashmap, *keys):
    if type(hashmap) is not mal.Hash:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected hash, received {}".format(type(hashmap)))

    new = hashmap.copy()
    for key in keys:
        new.pop(key, None)

    return mal.Hash(new)


def mal_get(hashmap, key):
    if hashmap == mal.NIL:
        hashmap = mal.Hash({})
    if type(hashmap) is not mal.Hash:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected hash, received {}".format(type(hashmap)))
    if key in hashmap:
        return hashmap[key]
    else:
        return mal.NIL


def mal_containsp(hashmap, key):
    if type(hashmap) is not mal.Hash:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected hash, received {}".format(type(hashmap)))
    if key in hashmap:
        return mal.Boolean(True)
    else:
        return mal.Boolean(False)


def mal_keys(hashmap):
    if type(hashmap) is not mal.Hash:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected hash, received {}".format(type(hashmap)))
    return mal.List(hashmap.keys())


def mal_vals(hashmap):
    if type(hashmap) is not mal.Hash:
        return mal.Error("TypeError",
                         "Wrong type argument: "
                         "expected hash, received {}".format(type(hashmap)))
    return mal.List(hashmap.values())


# metadata
def mal_meta(obj):
    try:
        data = obj.meta
    except AttributeError:
        return mal.NIL
    return data


def mal_with_meta(obj, data):
    new_obj = copy.copy(obj)
    try:
        new_obj.meta = data
    except AttributeError:
        return obj
    return new_obj


# time
def mal_time_ms():
    """Return the current time as miliseconds since the epoch.

    Note that depending on the system, this function may only provide an
    accuracy of 1 second.

    """
    return time.time() * 1000


# core namespace
ns = {'+':           mal.Builtin(mal_add),
      '-':           mal.Builtin(mal_substract),
      '*':           mal.Builtin(mal_multiply),
      '/':           mal.Builtin(mal_divide),

      '=':           mal.Builtin(mal_equal),
      '<':           mal.Builtin(mal_less),
      '<=':          mal.Builtin(mal_less_or_equal),
      '>':           mal.Builtin(mal_greater),
      '>=':          mal.Builtin(mal_greater_or_equal),

      'cons':        mal.Builtin(mal_cons),
      'concat':      mal.Builtin(mal_concat),
      'conj':        mal.Builtin(mal_conj),
      'nth':         mal.Builtin(mal_nth),
      'first':       mal.Builtin(mal_first),
      'rest':        mal.Builtin(mal_rest),
      'list':        mal.Builtin(mal_list),
      'list?':       mal.Builtin(mal_listp),
      'empty?':      mal.Builtin(mal_emptyp),
      'count':       mal.Builtin(mal_count),

      'pr-str':      mal.Builtin(mal_pr_str),
      'str':         mal.Builtin(mal_str),
      'prn':         mal.Builtin(mal_prn),
      'println':     mal.Builtin(mal_println),

      'read-string': mal.Builtin(reader.read_str),
      'slurp':       mal.Builtin(mal_slurp),

      'readline':    mal.Builtin(mal_readline),

      'atom':        mal.Builtin(mal_atom),
      'atom?':       mal.Builtin(mal_atomp),
      'deref':       mal.Builtin(mal_deref),
      'reset!':      mal.Builtin(mal_reset),

      'throw':       mal.Builtin(mal_throw),

      'apply':       mal.Builtin(mal_apply),
      'map':         mal.Builtin(mal_map),

      'symbol':      mal.Builtin(mal_symbol),
      'keyword':     mal.Builtin(mal_keyword),
      'vector':      mal.Builtin(mal_vector),
      'seq':         mal.Builtin(mal_seq),

      'nil?':        mal.Builtin(mal_nilp),
      'true?':       mal.Builtin(mal_truep),
      'false?':      mal.Builtin(mal_falsep),
      'symbol?':     mal.Builtin(mal_symbolp),
      'keyword?':    mal.Builtin(mal_keywordp),
      'vector?':     mal.Builtin(mal_vectorp),
      'map?':        mal.Builtin(mal_mapp),
      'sequential?': mal.Builtin(mal_sequentialp),
      'string?':     mal.Builtin(mal_stringp),
      'typeof':      mal.Builtin(mal_typeof),

      'hash-map':    mal.Builtin(mal_hashmap),
      'assoc':       mal.Builtin(mal_assoc),
      'dissoc':      mal.Builtin(mal_dissoc),
      'get':         mal.Builtin(mal_get),
      'contains?':   mal.Builtin(mal_containsp),
      'keys':        mal.Builtin(mal_keys),
      'vals':        mal.Builtin(mal_vals),

      'meta':        mal.Builtin(mal_meta),
      'with-meta':   mal.Builtin(mal_with_meta),

      'time-ms':     mal.Builtin(mal_time_ms)}
