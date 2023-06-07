# AlphaMatico 1


This project contains an implementation of multiple agents designed to solve
the game [Mathematico](https://github.com/balgot/mathematico). There are two
types of agents:
* pure Monte Carlo Tree Search
* *AlphaZero* adaptation

based on two different libraries:
* [`open_spiel`](https://github.com/deepmind/open_spiel)
* [`mcts`](https://github.com/pbsinclair42/MCTS) (custom AlphaZero implementation
uses only the Value Head).


## Requirements

This project was build using `Python 3.10` but should be able to support
`3.11>Python>=3.9` out-of-the-box.

Install the necessary packages:

```bash
pip install -r requirements.txt
```

## Usage

This project contains multiple files for different purposes:
* to **run the evaluation** and view the **results**, check out `evaluation/`
* to see **examples**, and the learning algorithms, **train an agent**,
    visit `notebooks/`
* to view the implementation, head to `src/`

See [Documentation](#documentation) below for further exaples.


## Documentation

In the last part, we will present the interface of both, `mathematico` and
this repository.


### 1. mathematico

The studied game, *Mathematico*, is part of another package. To install the game,
use:

```bash
pip install install --quiet 'git+https://github.com/balgot/mathematico.git#egg=mathematico&subdirectory=game'
```

In order to play the game, you need to supply a `Player` instance to the `Mathematico` object, e.g.:

```python
from mathematico import Mathematico, RandomPlayer

game = Mathematico()
player1 = RandomPlayer()
game.add_player(player1)
game.add_player(RandomPlayer())
# ... add as many players as needed
game.play()
```

which returns the achieved scores per specified players in the order, they
were added to the game.

For other options of installation (`Python < 3.9`), detailed rules explanation
and detailed interface options, refer to the [github repository](https://github.com/balgot/mathematico). See also `notebooks/mathematico.ipynb` for examples.


### 2. `open_spiel` Adaptation of `Mathematico`

To use `Mathematico` from the [`open_spiel`](https://github.com/deepmind/open_spiel)
(`pyspiel`) package, it is sufficient to import one package:

```python
import src.agents.ospiel  # registers the game automatically
import pyspiel

game = pyspiel.load_game("mathematico")
state = game.new_initial_state()
```

Check `notebooks.mcts_open_spiel.ipynb` for examples on how to use this.


### 3. MCTS Agents

There are two types of MCTS agent in this repository:
* customised Python implementation, inspired by [mcts](https://github.com/pbsinclair42/MCTS), see the corresponding class for further details:

```python
from src.agents.mcts_player import MctsPlayer

MAX_TIME = 500  # 500 ms per move
MAX_SIMULATIONS = 20  # 20 MCTS rollouts per move

custom_mcts_player = MctsPlayer(MAX_TIME, MAX_SIMULATIONS)
```

* `open_spiel` implementations, available as:

```python
from src.agents.ospiel import OpenSpielPlayer

MAX_SIMULATIONS = 20  # 20 MCTS rollouts per move

open_spiel_player = OpenSpielPlayer(MAX_SIMULATIONS)
```

### 4. Train `open_spiel` AlphaZero Agent

To train (customised `open_spiel`) AlphaZero agent, use script at
`src/train_azero.py`. This will require authentication for online logging,
you can disable this by defining environment variable `WANDB_MODE=offline`.

```bash
# to see help
python src/train_azero.py --help

# train default agent
python src/train_azero.py
```

#### 4.1 Loading trained agent

Assuming that the previous script saved the configuration and the checkpoints
to `PATH/` folder, it is possible to load the trained bot using:

```python
from azero import load_trained_bot as _load_azero_bot
import json
import os

PATH = "PATH/"
CHECKPOINT = -1

def load_trained_bot():
    with open(os.path.join(PATH, "config.json"), "r") as f:
        cfg = json.load(f)

    bot, _ = _load_azero_bot(cfg, PATH, CHECKPOINT, is_eval=True)
    return bot
```

The trained bot is not compatible with `mathematico` interface, it is
necessary to wrap it, for example by:

```python
from src.agents.ospiel import OpenSpielPlayer

MAX_SIMULATIONS = 20  # does not matter here, original (training) value will be used
player = OpenSpielPlayer(MAX_SIMULATIONS)
player.bot = bot
```

### 5. Train (Value Network Only) Agent

Use notebooks `notebooks/rf.ipynb` or `notebooks/rf-2.ipynb` to train
these agents.


### 6. Evaluation of Trained Agents

See `evaluation/perft.py` for detailed instructions and `evaluation/perft.sh`
for examples on how to use this script.


## License

Open source, see `LICENSE` file for further details.



## Authors

Samuel Gazda, Michal Barnišin