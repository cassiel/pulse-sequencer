"""
Wrapper for the new, python-based pulse sequencer.

p = fanout(p1, p2, p3, p4, notes.fire)
q = indexer(p, heldNotes, firstIf: x, ...)
q.fire(0)

$Id$
"""

from core.interfacing import Outputter
from core.basis import Context
from lib.chains import Assembler, Transposer, Ranger, Indexer, Selector
from lib.pulses import Sprayer, Cycler

c = Context()
outputter = Outputter(maxObject, c, 0, 0, 100)

# This is a port of the "Tangram" pattern from over a decade ago.

random_1 = Transposer(c, Ranger(c, 127), 1);

P0 = Assembler(c, 59, 61, 64, 54, 66);
P1 = Transposer(c, P0, 7);
P2 = Transposer(c, P0, 12);
P = Assembler(c, P0, P1, P2);

prefix_1 = Assembler(c, '111.00..')
prefix_2 = Assembler(c, '1.1100..')

prefix = Selector(c, Ranger(c, 3), prefix_1, prefix_1, prefix_2)

tail_1 = Assembler(c, '0.0..00.', '00000.1.', '0.0..10.')
tail_2 = Assembler(c, '0.0...0.', '1..00...', '0.0..00.')
tail = Selector(c, Ranger(c, 2), tail_1, tail_2)

inputPatt = Assembler(c, prefix, tail)

velocities = Assembler(c, 120, 80, random_1)

triggerPitch = Cycler(c, P, outputter.pitch, firstIf=1, nextIf='..', loopIf='..')
triggerVelocity = Cycler(c, velocities, outputter.velocity, firstIf=1, nextIf='..', loopIf='..')
fan = Sprayer(c, triggerPitch, triggerVelocity, outputter.emit)

# Main entry point:

input = Cycler(c, inputPatt, fan, firstIf=0, nextIf='..', loopIf='..')

def clock(i):
    c.tick()
    input.fire(i)
