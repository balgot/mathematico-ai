# Evaluation of Mathematico agents

This folder contains the scripts `perft.py` and `manual_play.py`
which can be used to measure the performance of one agent and compare
it against previously measured agents.


## Usage

To play a game and collect human results, use

    python manual_play.py --game N

where `N` is the number of the game to play, from the predefined
seeds, on which all the games are played. This script let's you
play a `pygame` mathematico, and prints the score with the final
time to console. It is the responsibility of the human player
to collect all **20** samples and store them in `data.csv` for
future analysis.

---

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


## Recommendations

For reproducibility, either set random seeds for each agent, or run the same
agent multiple times.

Keep a copy of the run code within this directory for future examination.
