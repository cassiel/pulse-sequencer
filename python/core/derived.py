from manifest import *
from core.basis import Const

def wrap(context, item):
    """
    Turn an item into a chain - including a Const.
    >>> wrap(None, 42)
    <core.basis.Const ...>

    >>> from const import C
    >>> context = C(get=Mock('get', returns=1))
    >>> chain = wrap(context, '1.2')
    >>> chain[2]
    Called get()
    2

    >>> from const import C
    >>> context = C(get=Mock('get', returns=1))
    >>> chain1 = wrap(context, '1.2')
    >>> chain2 = wrap(context, chain1)
    >>> chain2[2]
    Called get()
    2
    """
    if type(item) in [STRING_type, LIST_type, INTEGER_type, NONE_type]:
        return Const(context, item)
    else:
        return item

if __name__ == "__main__":
    import doctest
    from minimock import Mock
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
                               |doctest.ELLIPSIS
                               |doctest.NORMALIZE_WHITESPACE,
                    verbose=False
                   )
