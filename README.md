`-*- word-wrap: t; -*-`

pulse-sequencer
===============

# Usage

- From Live, load the main patcher device `PulseSeq.amxd`. Optionally do a "Collect and Save" in Live to put that into the Live Project. (You may well end up doing this anyway for audio and other assets.)

- The main device will probably not be able to see its sub-patchers, so open the (Max) Project of the device and add the `sub-patcher` directory to it (or add the sub-patchers to the Project explicitly).

- You can now, if you wish, "Consolidate" the Max Project to copy sub-patchers into it (in your `Documents` folder), or leave the sub-patchers where they are. In any case, the Max Project will be in `Documents` - Max for Live insists on this.

- To run the example sequence (in `main.py`), add the `python` directory to the Max Project's search path. A better solution is to follow the instructions at the top of `main.py`: do a `sys.path.append` to get the pulse sequencer itself, and then write a top-level script for each sequence.

# Unit Tests

Install `MiniMock`:

        sudo easy_install MiniMock==dev

Then:

        sh unit-tests.sh
