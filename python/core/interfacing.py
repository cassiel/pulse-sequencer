"""
Overall interface (including MIDI) for talking to the outside world.

$Id: interfacing.py,v 7a3432f42e77 2011/03/11 21:55:04 nick $
"""

from basis import Chain, Pulse

class KeyboardChain(Chain):
    """
    A chain which can hold the notes played/held on a keyboard. At present
    the notes are only in chronological order, and we only hold the pitches.
    Repeated notes are discarded.
    (We might change this at some stage to have it encapsulate individual
    chains for pitch and velocity.)
    """
    def __init__(self, context):
        Chain.__init__(self, context)
        self.__pitches = []

    def instance(self):
        return self.__pitches

    def noteOn(self, pitch, velocity):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> k = KeyboardChain(context)
        >>> k.noteOn(60, 64)
        >>> k.noteOn(72, 64)
        >>> k[0]
        Called get()
        60
        >>> k[1]
        Called get()
        72
        """
        if not pitch in self.__pitches:
            self.__pitches.append(pitch)

    def noteOff(self, pitch):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> k = KeyboardChain(context)
        >>> k.noteOn(60, 64)
        >>> k.noteOff(60)
        >>> {'a': k[0]}
        Called get()
        {'a': None}
        >>> k.noteOn(60, 64)
        >>> k.noteOn(72, 64)
        >>> k.noteOn(60, 64)
        >>> k.length()
        Called get()
        2
        >>> k[0]
        Called get()
        60
        >>> k[1]
        Called get()
        72
        >>> k.noteOff(60)
        >>> k[0]
        Called get()
        72
        >>> k.noteOff(72)
        >>> {'a': k[0]}
        Called get()
        {'a': None}
        """
        if pitch in self.__pitches:
            self.__pitches.remove(pitch)

    def allNotesOff(self):
        """
        >>> from const import C
        >>> context = C(get=Mock('get', returns=1))
        >>> k = KeyboardChain(context)
        >>> k.noteOn(60, 64)
        >>> k.allNotesOff()
        >>> {'a': k[0]}
        Called get()
        {'a': None}
        """
        self.__pitches = []

class MidiIntHolder(Pulse):
    """
    Holder of a MIDI note message integer. (We should really
    range-check it.)  When fired, it simple holds the value; our
    Outputter actually farms and outputs the values.
    """
    def __init__(self, context, initialValue):
        Pulse.__init__(self, context)
        self.__value = initialValue

    def doFire(self, i):
        '''
        >>> p = MidiIntHolder(None, 47)
        >>> p.get()
        47

        >>> p.fire(36)
        >>> p.get()
        36
        '''
        self.__value = i

    def get(self):
        return self.__value

class OutputterPulse(Pulse):
    """
    The Outputter pulse is a wrapper around an Outputter.
    """
    def __init__(self, context, outputter):
        Pulse.__init__(self, context)
        self.__outputter = outputter

    def doFire(self, _):
        """
        >>> from const import C
        >>> outputter = C(emitNote=Mock('emitNote'))
        >>> p = OutputterPulse(None, outputter)
        >>> p.fire(99)
        Called emitNote()
        """
        self.__outputter.emitNote()

class CtrlOutput(Pulse):
    """
    Pulse to send out CC messages.
    """
    def __init__(self, maxObject, context, cc_no):
        Pulse.__init__(self, context)
        self.__maxObject = maxObject
        self.__cc_no = cc_no

    def doFire(self, i):
        self.__maxObject.outletHigh(1, [self.__cc_no, i])

class Outputter:
    """
    Holder, and emitter, of bundled MIDI note messages. Wrapped around
    a collection of MidiIntHolders for an entire note. These can be
    picked up by our collection of pulses and chains, as can its
    fire() pulse to trigger the actual output.
    """
    def __init__(self, maxObject, context, pitch, velocity, duration):
        self.__maxObject = maxObject
        self.pitch = MidiIntHolder(context, pitch)
        self.velocity = MidiIntHolder(context, velocity)
        self.duration = MidiIntHolder(context, duration)
        self.emit = OutputterPulse(context, self)

    def emitNote(self):
        p = self.pitch.get()
        v = self.velocity.get()
        d = self.duration.get()
        self.__maxObject.outletHigh(0, [p, v, d])

if __name__ == "__main__":
    import doctest
    from minimock import Mock
    doctest.testmod(optionflags=doctest.REPORT_ONLY_FIRST_FAILURE
                               |doctest.ELLIPSIS
                               |doctest.NORMALIZE_WHITESPACE,
                    verbose=False
                   )
