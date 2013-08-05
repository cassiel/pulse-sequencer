"""
Basic chain and pulse functionality. It's here that we
do the occurs-check and make the chains idempotent (i.e.
returning the same value whenever examined in a single
call into the system).

$Id: basis.py,v 8377d61c2922 2011/03/19 22:35:25 nick $
"""

from core.util import flatten
import random

class Context:
    def __init__(self):
        self.__stamp = 0

    def tick(self):
        self.__stamp += 1

    def get(self):
        return self.__stamp

    def rand(self, lim):
        return random.randint(0, lim - 1)

class Chain:
    """
    A Chain is a list of numeric values or 'empty' slots.
    """
    def __init__(self, context):
        self.__context = context
        self.__lastStamp = -1

    def instance(self):
        """
        Soon: this will be the cached chain for each timestamp.
        """
        return []

    def __setupInstance(self):
        """ Get a new instance, if needed for a new timestamp.
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> c = Chain(context)
        >>> c.instance = Mock('instance', returns=[])
        >>> c._Chain__setupInstance()
        Called get()
        Called instance()
        >>> c._Chain__setupInstance()
        Called get()
        """
        stamp = self.__context.get()
        if stamp != self.__lastStamp:
            self.__instance = self.instance()
            self.__lastStamp = stamp

    def length(self):
        """
        TODO: occurs-check.
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> c = Chain(context)
        >>> c.instance = Mock('instance', returns=[1, 2])
        >>> c.length()
        Called get()
        Called instance()
        2
        >>> c.length()
        Called get()
        2
        >>> 
        """
        self.__setupInstance()
        return len(self.__instance)

    def __getitem__(self, key):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> c = Chain(context)
        >>> c.instance = Mock('instance', returns_iter=[[1, 2, 3]])
        >>> c[1]
        Called get()
        Called instance()
        2
        >>> c[1]
        Called get()
        2
        >>> context = C(get=Mock('get', returns_iter=[1, 2]))
        >>> c = Chain(context)
        >>> c.instance = Mock('instance', returns_iter=[[1, 2, 3], [4, 5, 6]])
        >>> c[1]
        Called get()
        Called instance()
        2
        >>> c[1]
        Called get()
        Called instance()
        5        
        """
        self.__setupInstance()
        if key < 0 or key >= len(self.__instance):
            return None
        else:
            return self.__instance[key]

    def __str__(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> x = Chain(context)
        >>> 
        >>> x.instance = Mock('instance', returns=[1, 3, None, -5])
        >>> print str(x)
        Called get()
        Called instance()
        [1 3 . -5]
        """
        self.__setupInstance()
        result = "["
        for v in self.__instance:
            if result != "[": result += " "
            if v is None:
                result += '.'
            else:
                result += str(v)
        result += "]"
        return result

class Pulse:
    '''
    A Pulse consumes incoming integer values in real time.
    '''
    def __init__(self, context):
        self.__context = context

    def fire(self, i):
        """ TODO: occurs-check, idempotence etc. """
        self.doFire(i)

    def doFire(self, i):
        '''
        Take an integer (probably from a global clock).
        '''
        pass

class Const(Chain):
    """
    A chain built from a (recursive) list, a string, or an int.
    It's here because a pervasive function (wrap)
    refers to it.
    """
    def __init__(self, context, v):
        Chain.__init__(self, context)
        self.__values = flatten(v)

    def instance(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))

        >>> c0 = Const(context, None)
        >>> {'a' : c0[0]}
        Called get()
        {'a': None}
        
        >>> c = Const(context, [1, 2, None, 3])
        >>> c[1]
        Called get()
        2

        >>> c[2] is None
        Called get()
        True

        >>> c[15] is None
        Called get()
        True

        >>> c[-5] is None
        Called get()
        True

        >>> c = Const(context, [5, '1.1'])
        >>> c[2] is None
        Called get()
        True

        >>> c[0]
        Called get()
        5

        >>> c[3]
        Called get()
        1

        >>> Const(context, '')[0] is None
        Called get()
        True

        >>> Const(context, [4])[0]
        Called get()
        4
        """
        return self.__values

if __name__ == "__main__":
    import doctest
    from minimock import Mock
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
                               |doctest.ELLIPSIS
                               |doctest.NORMALIZE_WHITESPACE,
                    verbose=False
                   )
