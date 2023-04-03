import os, sys
sys.path.append(os.path.join("../../"))

import math

from mathematico import Board, Player
from src.utils.mcts import MCTS
from ._mcts_state import Action, MathematicoState


_EXPLORATION = 1 / math.sqrt(2)


class MctsPlayer(Player):
    """
    MCTS player for the Mathematico game.

    Each time a decision about the next move is made, runs the MCTS
    with given resources contraints and finds the optimal move.

    Note: uses random policy for rollouts
    """

    def __init__(self,
        max_time_ms: int = 100,
        max_simulations: 'int | None' = None,
        exploration_constant: float = _EXPLORATION
    ):
        super().__init__()
        self.mcts = MCTS(max_time_ms, max_simulations, exploration_constant)

    def reset(self) -> None:
        self.board = Board()

    def move(self, number: int):
        state = MathematicoState(self.board, number)
        action: Action = self.mcts.search(state)[0]
        self.board.make_move(action, number)
