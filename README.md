# AlphaMatico 1


This project contains an implementation of a DRL (deep reinforcement learning) agent for the game [Mathematico](https://github.com/balgot/mathematico).


## Requirements

This project was build using `Python 3.11` but should be able to support
`Python>=3.9` out-of-the-box. If you want to test out the C++ example
of MCTS, *C++17*-compliant compiler will be necessary, see
`evaluation/cpp/Makefile` for details.


## Installation

Create the virtual environment and install the necessary packages:

```bash
python -m venv venv
source venv/bin/activate  # or ./venv/Scripts/activate
python -m pip install -U pip
python -m pip install 'git+https://github.com/balgot/mathematico.git#egg=mathematico&subdirectory=game'
python -m pip install -q torch pygame tabulate tqdm
python -m pip install -q jupyter  # or jupyterlab ... to run the notebooks
```


## Usage

This project contains multiple files for different purposes:
* to **run the evaluation** and view the **results**, check out `evaluation/`
* to see **examples**, and the learning algorithms, **train an agent**,
    visit `notebooks/`
* to view the implementation, head to `src/`


## License

Open source, see `LICENSE` file for further details.



## Authors

Samuel Gazda, Michal Barnišin
