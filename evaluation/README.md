# Evaluation of Mathematico agents

This folder contains the script `perft.py` which can be used to measure
the performance of one agent and compare it against previously measured
agents.


## Usage

To visualize the measured data, just run:

    python perft.py

These data are stored in `data.csv` local file in the form of:
* class name
* file from which it was imported
* optional descritpion of the run
* scores obtained per samples games (always the same 20 games)
* average time per game

To test a performance of an agent represented by classname `CLS` in a module
`MODULE`, just run:

    python perft.py --cls ${CLS} --file ${MODULE}

See `python perft.py --help` for more.


## Recommendations

For reproducibility, either set random seeds for each agent, or run the same
agent multiple times.

Keep a copy of the run code within this directory for future examination.
