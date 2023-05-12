# # Mathematico RL Agent

config = {
    "name": "leela-test-run",  # wandb-run name
    "cuda": True,  # use CUDA if possible (beware of memory)

    # random related, due to
    "seed": 0,
    "test_seed": 42,  # used for always measuring performance on the same games
    "test after . epochs": 50,  # how many epochs to train before conducting a tournament between agents

    "lr": 0.005,

    "simuls_limit": 100, # per move
    "policy repeats": 1, # how many times to rerun the rollout policy
    "static_policy": True, # if True, policy just returns the value of the node

    # algo params
    "test_games": 5,
    "n_simulated_games": 8,  # at least 2 for stddev to exist
    "sample": True,  # do random sampling from data or just shuffle, the only option due to RAM contraints
    "batch_size": 256,  # only applicable if "sample" = True
    "n_training_loops": 64, # per one RL epoch
    "n_epochs": 20_000
}


assert config["n_simulated_games"] > 1

import os, sys
sys.path.append(os.path.abspath(os.path.join("../")))

import random
import statistics
from copy import deepcopy
import time
import math
import warnings

import torch
from torchview import draw_graph
from torchsummary import summary
import numpy as np
from tqdm.notebook import trange, tqdm
import matplotlib.pyplot as plt

import wandb
wandb.init(config=config, project="PA026", name=config.get("name", None), settings=wandb.Settings(start_method="fork"))

import graphviz
graphviz.set_jupyter_format('png')  # VS code fix for cropped images from torchview

import mathematico
from src.utils import mcts
from src.utils.extract_data import extract
from src.utils.symmetries import all_symmetries
import src.nets as nets
from src.utils.lr import display_learning_rate


########################################
# random seed
########################################

torch.random.manual_seed(config["seed"])
random.seed(config["seed"])
np.random.seed(config["seed"])


########################################
# cuda settings
########################################

if not config["cuda"]:
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
dev = torch.device("cuda") if torch.cuda.is_available() and config["cuda"] else torch.device("cpu")
dev

from leela import LeelaNetwork
model = LeelaNetwork(5, 64, 8).to(dev)

optimizer = torch.optim.Adam(model.parameters(), lr=config["lr"])
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer)

# create fake input for testing the net and displaying the info
_board_batch = torch.tensor([[[0, 1, 11, 12, 13]] * 5] * 32, device=dev)
_out = model.forward(_board_batch)
print(summary(model, [(5, 5)], depth=7))

from src.agents.mcts_player import MctsPlayer, CardState, MoveState

def policy_static(state: mcts.StateI) -> float:
    board = torch.tensor([state.board.grid], device=dev)
    return model(board)


def policy_dynamic(state: mcts.StateI) -> float:
    _board = deepcopy(state.board)
    _possible_moves = set(_board.possible_moves())
    _deck = [k for k, v in state.deck.items() for _ in range(v)]
    random.shuffle(_deck)

    def mmove(move, card):
        b = deepcopy(_board.grid)
        b[move[0]][move[1]] = card
        return b

    with torch.no_grad():
        for i in range(len(_possible_moves)):
            batch = torch.tensor([
                mmove(move, _deck[i]) for move in _possible_moves
            ], device=dev)
            out = model(batch)
            idx = torch.argmax(out)
            move = list(_possible_moves)[idx]
            _board.make_move(move, _deck[i])
            _possible_moves.discard(move)
        return _board.score()



def repeated_dynamic(state):
    total = 0
    REPS = config['policy repeats']
    for _ in range(REPS):
        total += policy_dynamic(state)
    return total / REPS


agent = MctsPlayer(
    max_time_ms=None,
    max_simulations=config["simuls_limit"],
    policy=policy_static if config["static_policy"] else repeated_dynamic
)



def _log(start_time, mean, std, min_score, max_score, it, loss, loss_mcts, loss_final):
    # assert torch.isclose(loss_mcts + loss_final + loss_max, loss)

    duration = time.time() - start_time
    log_dict = {
        "time": duration,
        "mean": mean,
        "std": std,
        "min score": min_score,
        "max score": max_score,
        "loss": loss,
        "loss [mcts]": loss_mcts,
        "loss [final]": loss_final,
        "lr": optimizer.param_groups[0]['lr']  # valid only with one param group for optimizer
    }
    wandb.log(log_dict)



def learn_episode(agent: MctsPlayer, model: torch.nn.Module, n_games, batch_size, m_training):
    expert_memory = []

    # for logging..
    _scores = []
    loss = 0
    loss_mcts = 0
    loss_final = 0

    #############################################################################
    #                           playing phase
    #############################################################################

    model.eval()
    for game in trange(n_games, desc="Game playing phase", leave=None, position=1):
        agent.reset()
        cards = [i for i in range(1, 13+1) for _ in range(4)]
        random.shuffle(cards)

        # game memory - all states visited during mcts
        game_memory = []

        # which states were actually played
        true_states = []

        # play all the moves till the end
        for move in trange(5*5, desc="Playing moves", leave=None, position=2):
            state = deepcopy(agent.board.grid)
            card = cards[move]
            estimate, root = agent.move_(card)
            visited_states = extract(root)
            for b, e, v, d, h in visited_states:
                for s in all_symmetries(b):
                    game_memory.append((s, e, v, d, h))
            true_states.append(visited_states[0])

        final_score = agent.board.score()
        _scores.append(final_score)

        for board, exp, visits, depth, height in true_states:
            for s in all_symmetries(board):
                expert_memory.append((s, final_score, exp, visits, depth, height))
        for b, e, v, d, h in game_memory:
            expert_memory.append((b, None, e, v, d, h))


    #############################################################################
    #                           training phase
    #############################################################################

    model.train()
    weights = [entry[3] for entry in expert_memory]  # visit counts
    _s = sum(weights)
    weights = [w/_s for w in weights]
    indices = np.random.choice(len(expert_memory), size=(m_training, batch_size), replace=m_training*batch_size > len(expert_memory), p=weights)

    for train in trange(m_training, desc="Training loop", leave=None, position=1):
        batch = [expert_memory[idx] for idx in indices[train]]

        for with_final in (True, False):  # two passes, one for played states, one for hypothetical
            boards, reals, exps, viss, deps, heis = [], [], [], [], [], []
            for b, real, exp, vis, dep, hei in batch:
                if (real is not None) == with_final:
                    boards.append(b)
                    reals.append(real)
                    exps.append(exp)
                    viss.append(vis)
                    deps.append(dep)
                    heis.append(hei)

            if boards:

                optimizer.zero_grad()
                outs = torch.squeeze(model(torch.tensor(boards, device=dev)), dim=1)
                target = torch.tensor(exps, device=dev)

                _mcts_loss_norm = torch.log(torch.tensor(viss, device=dev) + 1) / (torch.tensor(heis, device=dev) + 1)
                _mcts_loss = torch.mean(_mcts_loss_norm * (target - outs)**2)

                _final_coef = (math.log(2) + 1) / (1 + torch.log(1 + torch.tensor(heis, device=dev)))
                _final_loss = 0 if not with_final else torch.mean(_final_coef * _mcts_loss_norm * (torch.tensor(reals, device=dev) - outs)**2)

                _loss = _mcts_loss + _final_loss

                if torch.any(torch.isnan(_loss)):
                    raise RuntimeError("NaN detected, instable learning..." + f"{_mcts_loss_norm=}\t{_mcts_loss=}\t{_final_loss=}")

                _loss.backward()
                optimizer.step()

                with torch.no_grad():
                    loss += _loss / m_training
                    loss_mcts += _mcts_loss / m_training
                    if with_final:
                        loss_final += _final_loss / m_training

    scheduler.step(loss_mcts)

    return (
        statistics.mean(_scores),
        statistics.stdev(_scores),
        min(_scores),
        max(_scores),
        loss,
        loss_mcts,
        loss_final
    )


# ## Training

START = time.time()

# _log(START, None, None, None, None, 0, None, None, None)
for epoch in trange(1, 1+config["n_epochs"], desc="Epochs"):
    mean, std, mini, maxi, L, Lm, Lf = learn_episode(
        agent,
        model,
        n_games=config["n_simulated_games"],
        batch_size=config["batch_size"],
        m_training=config["n_training_loops"]
    )


    if torch.any(torch.isnan(L)) or torch.any(torch.isnan(Lm)):
        print("Instabilities (NaN), aborting...")
        break
    _log(START, mean, std, mini, maxi, epoch, L, Lm, Lf)

    # form of early stopping
    if optimizer.param_groups[0]['lr'] < 1e-8:
        print(f"[{epoch=}] Learning rate is too low, aborting...")
        break

torch.save(model, "model.pt")
_log(START, None, None, None, None, 100*config['test after . epochs'], None, None, None)
wandb.finish()

# ## Evaluation
print("\nEvaluation\n==================\n\n")

import pprint

model.eval()
agent.reset()

cards = [i for i in range(1, 13+1) for _ in range(4)]
random.shuffle(cards)
true_states = []

# play all the moves till the end
for move in trange(5*5, desc="Playing moves", leave=True):
    state = deepcopy(agent.board.grid)
    card = cards[move]
    _, root = agent.move_(card)
    visited_states = extract(root)
    true_states.append(visited_states[0])

final_score = agent.board.score()
for board, exp, visits, depth, height in true_states:
    with torch.no_grad():
        print("\n\n")
        pprint.pprint(board)
        print(f"expected (mcts) score  {exp:>20.1f}")
        print(f"computed (vn) score    {model(torch.tensor([board], device=dev)).cpu().numpy()[0][0]:>20.1f}")
        print(f"game (true) score      {final_score:>20.1f}")
        print(f"{visits=}\t{depth=}\t{height=}")
