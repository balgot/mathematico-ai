"""This script loads trained agent from `notebooks/rf*.ipynb."""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import torch
import src.nets as nets
from src.agents.mcts_player import MctsPlayer
from src.utils.mcts import random_policy
from copy import deepcopy
import random


# edit these based on the trained agent config
dev = torch.device("cuda")
model = nets.LeelaNetwork(5, 64, 6).to(dev)
PATH = os.path.join(os.path.dirname(__file__), "leela-64-6.pt")

# load the model
model.load_state_dict(torch.load(PATH))


def policy_dynamic(state) -> float:
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


class TrainedAgent__20(MctsPlayer):
    def __init__(self):
        super().__init__(None, 20, policy=policy_dynamic)

class TrainedAgent__50(MctsPlayer):
    def __init__(self):
        super().__init__(None, 50, policy=policy_dynamic)

class TrainedAgent__100(MctsPlayer):
    def __init__(self):
        super().__init__(None, 100, policy=policy_dynamic)

class MixedAgent__20(MctsPlayer):
    def __init__(self):
        super().__init__(None, 20)

    def move_(self, number: int):
        if self.board.occupied_cells >= 20:
            self.mcts.rollout = random_policy
        else:
            self.mcts.rollout = policy_dynamic
        return super().move_(number)

class MixedAgent__50(MctsPlayer):
    def __init__(self):
        super().__init__(None, 50)

    def move_(self, number: int):
        if self.board.occupied_cells >= 20:
            self.mcts.rollout = random_policy
        else:
            self.mcts.rollout = policy_dynamic
        return super().move_(number)