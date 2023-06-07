# Evaluation of Mathematico agents

This folder contains the script `perft.py`
which can be used to measure the performance of one agent and compare
it against previously measured agents.


## Usage

To visualize the measured data, just run:

    python perft.py

These data are stored in `data.csv` local file in the form of:
* class name
* file from which it was imported
* optional descritpion of the run
* scores obtained per samples games (always the same 20 games)
* average time per game

---

To test a performance of an agent represented by classname `CLS` in a module
`MODULE`, just run:

    python perft.py --cls ${CLS} --file ${MODULE}

See `python perft.py --help` for more.


## Content

* `data_human_10--all.csv` contains the results 10 games which all human
evaluators played
* `data_human_20.csv` contains the results of the evalluation games (20)
of human evaluators who played all of them
* `perft.py` script to run evaluation
* `perft.sh` script to compare all available agents at once
* `*.py` classes with players to evaluate


## Recommendations

For reproducibility, either set random seeds for each agent, or run the same
agent multiple times. Ideally add commit hash to description via `--desc`.
