#!/bin/bash

for f in `find . -name '*.py'`; do
    if [[ $f != './main.py' ]]; then
	echo TEST $f
	PYTHONPATH=. python $f
    fi
done
