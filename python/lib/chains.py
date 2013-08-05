'''
Library chain generators and combination functions.

$Id: chains.py,v 82acc1b558e6 2011/03/23 22:03:28 nick $
'''

from core.basis import Chain
from core.derived import wrap

class Assembler(Chain):
    """
    A chain whose arguments are constants (each wrapped into
    a ConstChain) or objects which are assumed to be chains.
    """
    def __init__(self, context, *values):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> c = Assembler(context, 99)
        >>> c[0]
        Called get()
        Called get()
        Called get()
        99
        """
        Chain.__init__(self, context)
        self.__chains = [wrap(context, v) for v in values]

    def instance(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> c0 = Assembler(context, None)
        >>> {'a' : c0[0]}
        Called get()
        ...
        Called get()
        {'a': None}
        
        >>> c0 = Assembler(context, '5.6')
        >>> c = Assembler(context, 1, [2, 4], c0, None, 7)
        >>> c[2]
        Called get()
        ...
        Called get()
        4

        >>> c[3]
        Called get()
        5

        >>> {'a': c[6]}
        Called get()
        {'a': None}

        >>> c[7]
        Called get()
        7
        """
        result = []
        for c in self.__chains:
            result += [c[i] for i in range(c.length())]
        return result

class Transposer(Chain):
    """
    Transposer(c1, c2): c1 is transposed by c2[0], if the
    latter exists and is not None.
    """
    def __init__(self, context, sourceChain, xposeChain):
        Chain.__init__(self, context)
        self.__sourceChain = wrap(context, sourceChain)
        self.__xposeChain = wrap(context, xposeChain)

    def instance(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> print Transposer(context, [1, 2, None, 10], 30)
        Called get()
        ...
        [31 32 . 40]
        >>> print Transposer(context, [1, 2, None, 10], [])
        Called get()
        ...
        [1 2 . 10]
        >>> print Transposer(context, '9.9', '1')
        Called get()
        ...
        [10 . 10]
        """
        v = self.__xposeChain[0]
        if v is None: v = 0
        result = []
        for i in range(self.__sourceChain.length()):
            x = self.__sourceChain[i]
            result.append(None if x is None else x + v)
        return result

class Ranger(Chain):
    """
    Ranger(c) is a chain of length c[0] whose values,
    on each sampling sweep, range between 0 and c[1]-1.
    If c[0] is None or negative, returns []. If c[1]
    is None or <=0, returns a chain of None values.

    Special case: if c has one value, it is treated
    as [1, value] - randomised chains of length 1
    are quite useful.
    """
    def __init__(self, context, params):
        Chain.__init__(self, context)
        self.__params = wrap(context, params)

    def instance(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1), rand=Mock('rand', returns_iter=[1, 5, 2, 7, 9]))
        >>> print Ranger(context, [5, 10])
        Called get()
        ...
        Called rand(10)
        ...
        [1 5 2 7 9]
        >>> context = C(get=Mock('get', returns=1), rand=Mock('rand', returns_iter=[]))
        >>> print Ranger(context, [1, 0])
        Called get()
        ...
        [.]
        >>> context = C(get=Mock('get', returns=1), rand=Mock('rand', returns_iter=[]))
        >>> print Ranger(context, [1, None])
        Called get()
        ...
        [.]
        >>> context = C(get=Mock('get', returns=1), rand=Mock('rand', returns_iter=[]))
        >>> print Ranger(context, [None, 14])
        Called get()
        ...
        []
        >>> context = C(get=Mock('get', returns=1), rand=Mock('rand', returns_iter=[7]))
        >>> print Ranger(context, [14])
        Called get()
        ...
        [7]
        """
        len = self.__params[0]
        lim = self.__params[1]

        if self.__params.length() == 1:
            lim = len
            len = 1

        if len is None or len < 0: len = 0
        return [self.__random(lim) for i in range(len)]

    def __random(self, lim):
        if lim is None or lim <= 0:
            return None
        else:
            return self._Chain__context.rand(lim)

class Indexer(Chain):
    """
    Indexer(values, indices) is a chain the same length
    as indices, where each element is values[i] for indices
    value i. Value is None where i is None, i < 0, or i >= len(values).
    """
    def __init__(self, context, values, indices):
        Chain.__init__(self, context)
        self.__values = wrap(context, values)
        self.__indices = wrap(context, indices)

    def instance(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> print Indexer(context, [66, -6, None, 23], [0, 2, 1, 3, -1, 17, None, 3])
        Called get()
        ...
        [66 . -6 23 . . . 23]
        >>> print Indexer(context, '78.9', '0.1.2.1.3.0')
        Called get()
        ...
        [7 . 8 . . . 8 . 9 . 7]
        """
        return [self.__calc(self.__indices[i]) for i in range(self.__indices.length())]

    def __calc(self, offset):
        return None if offset is None else self.__values[offset]

class Selector(Chain):
    """
    Selector(s, c1 ... cn) returns one of c1, ..., cn per
    tick. depending on s[0] (from 0 to n-1). (This is why idempotence
    is important.) If s[0] is None or < 0 or >= n, returns [].
    """
    def __init__(self, context, index, *chains):
        Chain.__init__(self, context)
        self.__index = wrap(context, index)
        self.__chains = [wrap(context, c) for c in chains]

    def instance(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> print Selector(context, 1, [6, 7], [8, 9, 10], [3, 4])
        Called get()
        ...
        [8 9 10]
        >>> print Selector(context, -3, [6, 7], [8, 9, 10], [3, 4])
        Called get()
        ...
        []
        >>> print Selector(context, 17, [6, 7], [8, 9, 10], [3, 4])
        Called get()
        ...
        []
        >>> print Selector(context, [], [6, 7], [8, 9, 10], [3, 4])
        Called get()
        ...
        []
        """
        idx = self.__index[0]
        if idx is None or idx < 0 or idx >= len(self.__chains):
            return []
        else:
            chain = self.__chains[idx]
            return [chain[i] for i in range(chain.length())]

if __name__ == "__main__":
    import doctest
    from minimock import Mock
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
                               |doctest.ELLIPSIS
                               |doctest.NORMALIZE_WHITESPACE,
                    verbose=False
                   )
