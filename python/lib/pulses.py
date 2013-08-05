'''
Library pulse generators and combination functions.

$Id: pulses.py,v dd2b82f85230 2011/03/19 21:43:46 nick $
'''

from core.basis import Pulse, Const
from core.derived import wrap

class Sprayer(Pulse):
    def __init__(self, context, *pulses):
        """
        >>> from const import C
        >>> pulse1 = C(fire=Mock('fire1'))
        >>> pulse2 = C(fire=Mock('fire2'))
        >>> p = Sprayer(None, pulse1, pulse2)
        >>> p.fire(95)
        Called fire1(95)
        Called fire2(95)
        """
        Pulse.__init__(self, context)
        self.__pulses = list(pulses)

    def doFire(self, i):
        for p in self.__pulses: p.fire(i)

class Cycler(Pulse):
    """
    Our full-on chain-cycling pulse. Runs along a chain,
    outputting its values in turn to a destination pulse.
    Configuration args are:

        firstIf: <c> - reset to start of chain, and fire, if
        incoming pulse is between c[0] and c[1] inclusive.

        nextIf: <c> - if not firstIf(), then pre-advance
        position and fire if between c[0] and c[1] inclusive.

        loopIf: <c> - if nextIf(), and the counter has just
        gone past the end of the chain, wrap the counter
        by modulo(chain length) and fire if between c[0]
        and c[1].

    Interpretation of <c>: if [], fail. If a single
    value [None], fail. If [i], then match only i.
    If [i, j] then i<=x<=j, but treat None for i
    or j as open-ended. c[2] onwards ignored.
    If the keyword argument is totally absent, treat
    as [].
    """
    def __init__(self, context, chain, outPulse, **args):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> pulse = C()
        >>> cycler = Cycler(context, '123', pulse, firstIf=99)
        >>> cycler._Cycler__chain
        <core.basis.Const instance ...>
        >>> print cycler._Cycler__firstIf
        Called get()
        [99]
        >>> cycler._Cycler__firstIf[0]
        Called get()
        99
        >>> cycler = Cycler(context, '123', None, firstIf=0)
        >>> print cycler._Cycler__firstIf
        Called get()
        [0]
        >>> cycler = Cycler(context, '123', pulse)
        >>> {'a': cycler._Cycler__firstIf[0]}
        Called get()
        {'a': None}
        """
        Pulse.__init__(self, context)
        self.__chain = wrap(context, chain)
        self.__outPulse = outPulse
        fi = args.get('firstIf')
        self.__firstIf = wrap(context, fi) if fi is not None else Const(context, [])
        ni = args.get('nextIf')
        self.__nextIf = wrap(context, ni) if ni is not None else Const(context, [])
        li = args.get('loopIf')
        self.__loopIf = wrap(context, li) if li is not None else Const(context, [])
        self.__counter = 0

    def __inRange(self, value, rangeChain):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> cycle = Cycler(context, None, None)
        >>> cycle._Cycler__inRange(2, Const(context, ''))
        Called get()
        False
        >>> cycle._Cycler__inRange(2, Const(context, [1, 3]))
        Called get()
        ...
        True
        >>> cycle._Cycler__inRange(3, Const(context, [1, 2]))
        Called get()
        ...
        False
        >>> cycle._Cycler__inRange(None, Const(context, [1, 2]))
        False
        >>> cycle._Cycler__inRange(37, Const(context, '0.'))
        Called get()
        ...
        True
        >>> cycle._Cycler__inRange(6, Const(context, '.9'))
        Called get()
        ...
        True
        >>> cycle._Cycler__inRange(6, Const(context, '..'))
        Called get()
        ...
        True
        >>> cycle._Cycler__inRange(37, Const(context, 37))
        Called get()
        ...
        True
        >>> cycle._Cycler__inRange(37, Const(context, 36))
        Called get()
        ...
        False
        """
        if value is None:
            return False
        elif rangeChain.length() == 0:
            return False
        elif rangeChain.length() == 1:
            return (value == rangeChain[0])
        else:
            lo = rangeChain[0]
            hi = rangeChain[1]
            return (lo is None or value >= lo) and (hi is None or value <= hi)

    def doFire(self, i):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> pulse = C(fire=Mock('fire'))
        >>> cycler = Cycler(context, '723', pulse, firstIf=0)
        >>> cycler.fire(0)
        Called get()
        ...
        Called fire(7)
        >>> cycler.fire(1)
        Called get()
        ...
        >>> cycler.fire(2)
        Called get()
        ...
        >>> cycler.fire(0)
        Called get()
        ...
        Called fire(7)

        >>> cycler = Cycler(context, '923', pulse, firstIf='..')
        >>> cycler.fire(0)
        Called get()
        ...
        Called fire(9)
        >>> cycler.fire(1)
        Called get()
        ...
        Called fire(9)
        >>> cycler.fire(2)
        Called get()
        ...
        Called fire(9)
        """
        length = self.__chain.length()
        if length > 0:
            if self.__inRange(i, self.__firstIf):
                self.__counter = 0
                self.__doit()
            elif self.__inRange(i, self.__nextIf):
                self.__counter += 1

                if self.__counter < length:
                    self.__doit()
                elif self.__inRange(i, self.__loopIf):
                    self.__counter %= length
                    self.__doit()

    def __doit(self):
        n = self.__chain[self.__counter]
        if n is not None: self.__outPulse.fire(n)

if __name__ == "__main__":
    import doctest
    from minimock import Mock
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
                               |doctest.ELLIPSIS
                               |doctest.NORMALIZE_WHITESPACE,
                    verbose=False
                   )
