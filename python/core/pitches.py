'''
Useful musical constants.
'''

from const import C

# Start at "first" == 1:
INTERVALS = C(MAJOR=[None, 0, 2, 4, 5, 7, 9, 11, 12],
              MINOR=[None, 0, 2, 3, 5, 7, 8, 10, 12])

PITCHES=C(C=0,
          Cs=1, Db=1,
          D=2,
          Ds=3, Eb=3,
          E=4,
          F=5,
          Fs=6, Gb=6,
          G=7,
          Gs=8, Ab=8,
          A=9,
          As=10, Bb=10,
          B=11)

# MIDI octaves:

def OCTAVE(i):
    return (i + 2) * 12
