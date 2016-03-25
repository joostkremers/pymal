from mal_types import *


class MalEnv():
    """Mal environment class.

    An environment mapping symbols to Mal objects. Note that the symbols should
    be strings, not Mal objects, although the initializer accepts both strings
    naming symbols and mal_types.Symbol.

    """

    def __init__(self, outer=None, data=None, binds=[], exprs=[]):
        self.outer = outer

        if data is None:
            self.data = {}
        else:
            self.data = data

        for i in range(len(binds)):
            if type(binds[i]) is MalSymbol:
                sym = binds[i].name
            else:
                sym = binds[i]

            if sym == '&':
                sym = binds[i+1]
                val = list(exprs)[i:]
                self.set(sym, val)
                break

            else:
                if i < len(exprs):
                    val = exprs[i]
                else:
                    val = MalNil()

            self.set(sym, val)

    def set(self, symbol, value):
        if type(symbol) is MalSymbol:
            symbol = symbol.name
        if type(symbol) is str:
            self.data[symbol] = value
            return value
        else:
            return MalError("TypeError", "Cannot bind to non-symbol")

    def find(self, symbol):
        if type(symbol) is MalSymbol:
            symbol = symbol.name
        if symbol in self.data:
            return self
        elif self.outer is None:
            return None
        else:
            return self.outer.find(symbol)

    def get(self, symbol):
        if type(symbol) is MalSymbol:
            symbol = symbol.name
        env = self.find(symbol)
        if env:
            return env.data[symbol]
        else:
            return MalError("SymbolError",
                            "Symbol value is void '{}'".format(symbol))
