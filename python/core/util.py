from manifest import *
import string

def flatten(item):
    """
    Turn the item (a string, an int, or recursively a list of items)
    into an int/None list.
    
    >>> flatten('123')
    [1, 2, 3]
        
    >>> flatten('1.2.3')
    [1, None, 2, None, 3]

    >>> flatten([1, 2])
    [1, 2]

    >>> flatten(['12', '34'])
    [1, 2, 3, 4]

    >>> flatten([1, [2, [3, [4, 5], 6], 7], 8])
    [1, 2, 3, 4, 5, 6, 7, 8]

    >>> flatten(5)
    [5]

    >>> flatten('$@%^&$@')
    Traceback (most recent call last):
        ...
    SyntaxError: $@%^&$@
    """
    if type(item) == STRING_type:
        result = []
        for ch in item:
            if ch in string.digits:
                result.append(ord(ch) - ord('0'))
            elif ch == '.':
                result.append(None)
            else:
                raise SyntaxError(item)

        return result
    elif type(item) == LIST_type:
        x = []
        for i in item: x += flatten(i)
        return x
    else:
        return [item]

if __name__ == "__main__":
    import doctest
    from minimock import Mock
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
                               |doctest.ELLIPSIS
                               |doctest.NORMALIZE_WHITESPACE,
                    verbose=False
                   )

