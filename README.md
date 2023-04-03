# AlphaMatico 1


This project contains an implementation of a DRL (deep reinforcement learning) agent for the game [Mathematico](https://github.com/balgot/mathematico).


## Installation

Create the virtual environment and install the necessary packages:

```bash
python -m venv venv
source venv/bin/activate  # or ./venv/Scripts/activate
python -m pip install -U pip
python -m pip install 'git+https://github.com/balgot/mathematico.git#egg=mathematico&subdirectory=game'
python -m pip install torch pygame tabulate tqdm
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
