class MalType:
    """Parent type of all Mal-specific types."""

    # This makes it easier to define certain properties that apply to all or
    # most types, such as equality.

    # We can use MalType when we need to have an object that has no effect
    # whatsoever. VALUE in this case can indicate why this object exists. We do
    # this with comments, for example.
    def __init__(self, object):
        self.value = object

    def __str__(self):
        return ""

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.value == other.value)


class MalNil(MalType):
    """Mal nil type."""

    def __init__(self):
        self.value = None

    def __str__(self):
        return "nil"


class MalVector(MalType):
    """Mal vector type."""

    def __init__(self, value=None):
        if value is None:
            self.value = []
        else:
            self.value = value

    def __str__(self):
        items = [str(s) for s in self.value]
        return '[' + ' '.join(items) + ']'

    def __eq__(self, other):
        if type(self) is MalVector:
            val1 = self.value
        else:
            val1 = self
        if type(other) is MalVector:
            val2 = other.value
        else:
            val2 = other

        return val1 == val2

    def __len__(self):
        return len(self.value)

    def __contains__(self, x):
        return x in self.value

    def __getitem__(self, x):
        return self.value[x]


class MalSymbol(MalType):
    """Mal symbol type."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Mal Symbol object '{}'>".format(self.name)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.name == other.name)


class MalError(MalType):
    """Mal error type.

    Errors are returned as normal values, but they halt evaluation and are
    immediately returned to the top level.
    """

    def __init__(self, error_type, descr):
        self.error = error_type
        self.descr = descr

    def __str__(self):
        return self.error + ": " + self.descr

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


class MalKeyword(MalType):
    """Mal keyword type. """

    def __init__(self, name):
        """Create a keyword.

        Keywords are strings that start with a colon. If NAME does not start
        with a colon, one is added.
        """
        if name[0] != ":":
            name = ':' + name
        self.name = name

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.name == other.name)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class MalBuiltin(MalType):
    """Mal builtin function type."""

    def __init__(self, fn=None):
        self.fn = fn

    def __str__(self):
        return "#<Builtin function at {}>".format(hex(id(self)))


class MalFunction(MalType):
    """Mal function type."""

    def __init__(self, fn=None, params=None, ast=None, env=None,
                 is_macro=False, meta=None):
        self.fn = fn
        self.params = params
        self.ast = ast
        self.env = env
        self.is_macro = is_macro
        if meta is None:
            self.meta = MalNil()
        else:
            self.meta = meta

    def __str__(self):
        if self.is_macro:
            fn_type = "macro"
        else:
            fn_type = "funcion"
        return "#<User {} at {}>".format(fn_type, hex(id(self)))


class MalBoolean(MalType):
    """Mal boolean type."""

    def __init__(self, value=False):
        # We check for False with 'is', because in Python, 0 is equal to, but
        # not identical with, False, while in Mal, 0 counts as true.
        if value in [[], "", MalVector([]), MalNil(), {}] or value is False:
            self.value = False
        else:
            self.value = True

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return (self.value is other.value)

    def __str__(self):
        if self.value is True:
            return "true"
        if self.value is False:
            return "false"


class MalAtom(MalType):
    """Mal atom type."""

    def __init__(self, value=None):
        if value is None:
            self.value = MalNil()
        else:
            self.value = value

    def set(self, value):
        self.value = value

    def __str__(self):
        return '(atom {})'.format(self.value)
