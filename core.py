import copy
import time
import numbers

from  mal_types import *
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
        return MalError("ArgError", "'+': Wrong type argument")

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
        return MalError("ArgError", "'-': Wrong type argument")

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
        return MalError("ArgError", "'*': Wrong type argument")

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
        return MalError("ArithmeticError", "Division by zero")
    except TypeError:
        return MalError("ArgError", "'/': Wrong type argument")

    return first


# comparison functions
def mal_equal(*args):
    first = args[0]
    for arg in args[1:]:
        if arg != first:
            return MalBoolean(False)

    return MalBoolean(True)


def mal_less(*args):
    for i in range(len(args)-1):
        if not isinstance(args[i], numbers.Number):
            return MalError("ArgError",
                            "Wrong type argument: "
                            "expected number, got {}".format(type(args[i])))
        if not args[i] < args[i+1]:
            return MalBoolean(False)
    return MalBoolean(True)


def mal_less_or_equal(*args):
    for i in range(len(args)-1):
        if not isinstance(args[i], numbers.Number):
            return MalError("ArgError",
                            "'<=': Wrong type argument: "
                            "expected number, got {}".format(type(args[i])))
        if not args[i] <= args[i+1]:
            return MalBoolean(False)
    return MalBoolean(True)


def mal_greater(*args):
    for i in range(len(args)-1):
        if not isinstance(args[i], numbers.Number):
            return MalError("ArgError",
                            "'>': Wrong type argument: "
                            "expected number, got {}".format(type(args[i])))
        if not args[i] > args[i+1]:
            return MalBoolean(False)
    return MalBoolean(True)


def mal_greater_or_equal(*args):
    for i in range(len(args)-1):
        if not isinstance(args[i], numbers.Number):
            return MalError("ArgError",
                            "'>=': Wrong type argument: "
                            "expected number, got {}".format(type(args[i])))
        if not args[i] >= args[i+1]:
            return MalBoolean(False)
    return MalBoolean(True)


# list / vector functions
def mal_cons(obj, lst):
    if type(lst) is MalVector:
        lst = lst.value
    if type(lst) is not list:
        return MalError("ArgError", "'cons': Wrong type argument: "
                        "expected list or vector, got {}".format(type(lst)))
    return [obj] + lst


def mal_concat(*args):
    res = []
    for arg in args:
        if type(arg) is MalVector:
            res.extend(arg.value)
        elif type(arg) is list:
            res.extend(arg)
        else:
            return MalError("ArgError", "'concat': Wrong type argument: "
                            "expected list or vector, got {}".
                            format(type(arg)))

    return res


def mal_conj(seq, *elems):
    """Add ELEMS to SEQ (a list or vector).

    If SEQ is a list, the elements in ELEMS are added to the front of the list
    in reverse order. If SEQ is a vector, the elements are added to the end.

    """
    if not isinstance(seq, (list, MalVector)):
        return MalError("ArgError", "'conj': Wrong type argument:"
                        "expected list or vector, received {}".
                        format(type(seq)))

    if type(seq) is list:
        return list(elems)[::-1] + seq

    if type(seq) is MalVector:
        return MalVector(seq.value + list(elems))


def mal_nth(arg, index):
    if not isinstance(arg, (list, MalVector)):
        return MalError("ArgError", "'nth': Wrong type argument:"
                        "expected list or vector, received {}".
                        format(type(arg)))
    if index >= len(arg):
        return MalError("IndexError", "Index out of range")

    return arg[index]


def mal_first(arg):
    if not isinstance(arg, (list, MalVector, MalNil)):
        return MalError("ArgError", "'nth': Wrong type argument:"
                        "expected list or vector, received {}".
                        format(type(arg)))

    if type(arg) is MalNil or len(arg) == 0:
        return MalNil()

    return arg[0]


def mal_rest(arg):
    if not isinstance(arg, (list, MalVector, MalNil)):
        return MalError("ArgError", "'nth': Wrong type argument:"
                        "expected list or vector, received {}".
                        format(type(arg)))

    if type(arg) is MalNil:
        return []

    return arg[1:]


def mal_list(*args):
    return list(args)


def mal_listp(arg):
    if type(arg) is list:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_emptyp(arg):
    if type(arg) is MalVector:
        arg = arg.value
    if type(arg) is not list:
        return MalError("ArgError",
                        "'empty?': Wrong type argument: "
                        "expected list or vector, got {}".format(type(arg)))

    if arg == []:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_count(arg):
    if type(arg) is MalNil:
        return 0
    if type(arg) is MalVector:
        arg = arg.value
    if type(arg) is not list:
        return MalError("ArgError",
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
    return MalNil()


def mal_println(*args):
    print(" ".join([printer.pr_str(arg, False) for arg in args]))
    return MalNil()


# file functions
def mal_slurp(filename):
    try:
        f = open(filename, 'r')
        conts = f.read()
    except FileNotFoundError:
        return MalError("FileError", "File not found")
    return conts


# readline
def mal_readline(prompt):
    try:
        line = input(prompt)
    except EOFError:
        return MalNil()
    return line


# atom functions
def mal_atom(object):
    return MalAtom(object)


def mal_atomp(object):
    if type(object) is MalAtom:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_deref(atom):
    if type(atom) is not MalAtom:
        return MalError("TypeError",
                        "Expected atom, received {}".format(type(atom)))
    else:
        return atom.value


def mal_reset(atom, value):
    if type(atom) is not MalAtom:
        return MalError("TypeError",
                        "Expected atom, received {}".format(type(atom)))
    else:
        atom.set(value)
        return value


# throw
def mal_throw(arg):
    return MalError("UserError", arg)


# functional functions
def mal_apply(fn, *args):
    if not isinstance(fn, (MalBuiltin, MalFunction)):
        return MalError("TypeError", "'apply': Expected function,"
                        " received {}".format(fn))

    lastarg = args[-1]
    if type(lastarg) is MalVector:
        lastarg = lastarg.value

    if not isinstance(lastarg, list):
        return MalError("TypeError", "'apply': Expected list or vector,"
                        " received {}".format(args[-1]))

    allargs = list(args[:-1]) + lastarg

    return fn.fn(*allargs)


def mal_map(fn, lst):
    if not isinstance(fn, (MalBuiltin, MalFunction)):
        return MalError("TypeError", "'map': Expected function,"
                        " received {}".format(fn))

    if type(lst) is MalVector:
        lst = lst.value
    if type(lst) is not list:
        return MalError("TypeError", "Expected list or vector,"
                        " received {}".format(lst))

    res = []
    for elem in lst:
        evalled = fn.fn(elem)
        if type(evalled) is MalError:
            return evalled
        res.append(evalled)

    return res


# type functions
def mal_symbol(arg):
    if type(arg) is not str:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected string, received {}".format(arg))
    return MalSymbol(arg)


def mal_keyword(arg):
    if type(arg) is MalKeyword:
        return arg
    if type(arg) is not str:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected string, received {}".format(type(arg)))
    return MalKeyword(arg)


def mal_vector(*args):
    return MalVector(list(args))


def mal_seq(arg):
    """Turn ARG into a list.

    If ARG is nil or an empty list, vector or string, return nil. If ARG is a
    non-empty list, return it unchanged; if ARG is a non-empty vector, convert
    it to a list; if ARG is a non-empty string, return a list of characters.

    """
    if type(arg) is MalNil:
        return MalNil()

    if len(arg) == 0:
        return MalNil()

    if type(arg) is list:
        return arg

    if type(arg) is MalVector:
        return arg.value

    if type(arg) is str:
        return list(arg)

    # if all fails, return an error
    return MalError("ArgError", "'seq': Wrong type argument: "
                    "expected sequence, received {}".format(type(arg)))


# type predicates
def mal_nilp(arg):
    if arg == MalNil():
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_truep(arg):
    if arg == MalBoolean(True):
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_falsep(arg):
    if arg == MalBoolean(False):
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_symbolp(arg):
    if type(arg) is MalSymbol:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_keywordp(arg):
    if type(arg) is MalKeyword:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_vectorp(arg):
    if type(arg) is MalVector:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_mapp(arg):
    if type(arg) is dict:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_sequentialp(arg):
    if isinstance(arg, (list, MalVector)):
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_stringp(arg):
    if type(arg) is str:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


# hash functions
def mal_hashmap(*args):
    return reader.create_hash(args)


def mal_assoc(hashmap, *args):
    if type(hashmap) is not dict:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected hash, received {}".format(type(hashmap)))
    orig = hashmap.copy()

    new = reader.create_hash(list(args))
    if type(new) is MalError:
        return new

    orig.update(new)
    return orig


def mal_dissoc(hashmap, *keys):
    if type(hashmap) is not dict:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected hash, received {}".format(type(hashmap)))

    new = hashmap.copy()
    for key in keys:
        new.pop(key, None)

    return new


def mal_get(hashmap, key):
    if hashmap == MalNil():
        hashmap = {}
    if type(hashmap) is not dict:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected hash, received {}".format(type(hashmap)))
    if key in hashmap:
        return hashmap[key]
    else:
        return MalNil()


def mal_containsp(hashmap, key):
    if type(hashmap) is not dict:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected hash, received {}".format(type(hashmap)))
    if key in hashmap:
        return MalBoolean(True)
    else:
        return MalBoolean(False)


def mal_keys(hashmap):
    if type(hashmap) is not dict:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected hash, received {}".format(type(hashmap)))
    return list(hashmap.keys())


def mal_vals(hashmap):
    if type(hashmap) is not dict:
        return MalError("TypeError",
                        "Wrong type argument: "
                        "expected hash, received {}".format(type(hashmap)))
    return list(hashmap.values())


# metadata
def mal_meta(obj):
    try:
        data = obj.meta
    except AttributeError:
        return MalNil()
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
ns = {'+':           MalBuiltin(mal_add),
      '-':           MalBuiltin(mal_substract),
      '*':           MalBuiltin(mal_multiply),
      '/':           MalBuiltin(mal_divide),

      '=':           MalBuiltin(mal_equal),
      '<':           MalBuiltin(mal_less),
      '<=':          MalBuiltin(mal_less_or_equal),
      '>':           MalBuiltin(mal_greater),
      '>=':          MalBuiltin(mal_greater_or_equal),

      'cons':        MalBuiltin(mal_cons),
      'concat':      MalBuiltin(mal_concat),
      'conj':        MalBuiltin(mal_conj),
      'nth':         MalBuiltin(mal_nth),
      'first':       MalBuiltin(mal_first),
      'rest':        MalBuiltin(mal_rest),
      'list':        MalBuiltin(mal_list),
      'list?':       MalBuiltin(mal_listp),
      'empty?':      MalBuiltin(mal_emptyp),
      'count':       MalBuiltin(mal_count),

      'pr-str':      MalBuiltin(mal_pr_str),
      'str':         MalBuiltin(mal_str),
      'prn':         MalBuiltin(mal_prn),
      'println':     MalBuiltin(mal_println),

      'read-string': MalBuiltin(reader.read_str),
      'slurp':       MalBuiltin(mal_slurp),

      'readline':    MalBuiltin(mal_readline),

      'atom':        MalBuiltin(mal_atom),
      'atom?':       MalBuiltin(mal_atomp),
      'deref':       MalBuiltin(mal_deref),
      'reset!':      MalBuiltin(mal_reset),

      'throw':       MalBuiltin(mal_throw),

      'apply':       MalBuiltin(mal_apply),
      'map':         MalBuiltin(mal_map),

      'symbol':      MalBuiltin(mal_symbol),
      'keyword':     MalBuiltin(mal_keyword),
      'vector':      MalBuiltin(mal_vector),
      'seq':         MalBuiltin(mal_seq),

      'nil?':        MalBuiltin(mal_nilp),
      'true?':       MalBuiltin(mal_truep),
      'false?':      MalBuiltin(mal_falsep),
      'symbol?':     MalBuiltin(mal_symbolp),
      'keyword?':    MalBuiltin(mal_keywordp),
      'vector?':     MalBuiltin(mal_vectorp),
      'map?':        MalBuiltin(mal_mapp),
      'sequential?': MalBuiltin(mal_sequentialp),
      'string?':     MalBuiltin(mal_stringp),

      'hash-map':    MalBuiltin(mal_hashmap),
      'assoc':       MalBuiltin(mal_assoc),
      'dissoc':      MalBuiltin(mal_dissoc),
      'get':         MalBuiltin(mal_get),
      'contains?':   MalBuiltin(mal_containsp),
      'keys':        MalBuiltin(mal_keys),
      'vals':        MalBuiltin(mal_vals),

      'meta':        MalBuiltin(mal_meta),
      'with-meta':   MalBuiltin(mal_with_meta),

      'time-ms':     MalBuiltin(mal_time_ms)}
