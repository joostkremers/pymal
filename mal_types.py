class MalNil():
    """Mal nil type."""

    def __init__(self):
        self.value = None

    def __repr__(self):
        return "nil"


# There is only one nil value
MAL_NIL = MalNil()


class MalList(list):
    """Mal list type."""

    def __init__(self, value=[], meta=None):
        super(MalList, self).__init__(value)
        if meta is None:
            meta = MAL_NIL
        self.meta = meta

    def __repr__(self):
        items = [s.__repr__() for s in self]
        return '(' + ' '.join(items) + ')'

    def __str__(self):
        items = [str(s) for s in self]
        return '(' + ' '.join(items) + ')'


class MalVector(list):
    """Mal vector type."""

    def __init__(self, value=None, meta=None):
        super(MalVector, self).__init__(value)
        if meta is None:
            meta = MAL_NIL
        self.meta = meta

    def __repr__(self):
        items = [s.__repr__() for s in self]
        return '[' + ' '.join(items) + ']'

    def __str__(self):
        items = [str(s) for s in self]
        return '[' + ' '.join(items) + ']'


class MalHash(dict):
    """Mal hash table type."""

    def __init__(self, value=None, meta=None):
        if value is None:
            value = {}
        super(MalHash, self).__init__(value)
        if meta is None:
            meta = MAL_NIL
        self.meta = meta

    def __repr__(self):
        str_list = []
        for key, value in self.items():
            str_list += [key.__repr__(), value.__repr__()]
        return '{' + ' '.join(str_list) + '}'

    def __str__(self):
        str_list = []
        for key, value in self.items():
            str_list += [str(key), str(value)]
        return '{' + ' '.join(str_list) + '}'


class MalError():
    """Mal error type.

    Errors are returned as normal values, but they halt evaluation and are
    immediately returned to the top level.
    """

    def __init__(self, error_type, descr):
        self.error = error_type
        self.descr = descr

    def __repr__(self):
        return self.descr

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return ((self.error_type == other.error_type) and
                self.descr == other.descr)


class MalHandledError(MalError):
    """Mal handled error type.

    Errors handled by 'try*/catch*' are passed as handled errors, so that they
    do not halt evaluation.
    """

    def __init__(self, error_object):
        self.error = error_object.error
        self.descr = error_object.descr


# class MalString():
#     """Mal string type."""

#     def __init__(self, value="", meta=None):
#         self.value = value
#         if meta is None:
#             meta = MAL_NIL
#         self.meta = meta

#     def __repr__(self):
#         string = self.value
#         string = string.replace('\\', r'\\')
#         string = string.replace('\n', r'\n')
#         string = string.replace('"', r'\"')
#         string = '"' + string + '"'
#         return string

#     def __str__(self):
#         return self.value


class MalSymbol():
    """Mal symbol type."""

    def __init__(self, name, meta=None):
        self.name = name
        if meta is None:
            meta = MAL_NIL
        self.meta = meta

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.name == other.name)


class MalKeyword():
    """Mal keyword type. """

    def __init__(self, name, meta=None):
        """Create a keyword.

        Keywords are strings that start with a colon. If NAME does not start
        with a colon, one is added.
        """
        if name[0] != ":":
            name = ':' + name
        self.name = name
        if meta is None:
            meta = MAL_NIL
        self.meta = meta

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.name == other.name)

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class MalBuiltin():
    """Mal builtin function type."""

    def __init__(self, fn=None, meta=None):
        self.fn = fn
        if meta is None:
            meta = MAL_NIL
        self.meta = meta

    def __repr__(self):
        return "#<Builtin function at {}>".format(hex(id(self)))


class MalFunction():
    """Mal function type."""

    def __init__(self, fn=None, params=None, ast=None, env=None,
                 is_macro=False, meta=None):
        self.fn = fn
        self.params = params
        self.ast = ast
        self.env = env
        self.is_macro = is_macro
        if meta is None:
            meta = MAL_NIL
        self.meta = meta

    def __repr__(self):
        if self.is_macro:
            fn_type = "macro"
        else:
            fn_type = "function"
        return "#<User {} at {}>".format(fn_type, hex(id(self)))


class MalBoolean():
    """Mal boolean type."""

    def __init__(self, value=False):
        # We check for False with 'is', because in Python, 0 is equal to, but
        # not identical with, False, while in Mal, 0 counts as true.
        if value in [[], "", MalVector([]), MAL_NIL, {}] or value is False:
            self.value = False
        else:
            self.value = True

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.value is other.value)

    def __repr__(self):
        if self.value is True:
            return "true"
        if self.value is False:
            return "false"


class MalAtom():
    """Mal atom type."""

    def __init__(self, value=None):
        if value is None:
            value = MAL_NIL
        self.value = value

    def set(self, value):
        self.value = value

    def __repr__(self):
        return ('(atom ' + self.value.__repr__() + ')')

    def __str__(self):
        return ('(atom ' + self.value.__str__() + ')')
