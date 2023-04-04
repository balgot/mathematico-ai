import os, sys
sys.path.append(os.path.join("../../"))

import math

from mathematico import Board, Player
from src.utils.mcts import MCTS
from ._mcts_state import MoveState, CardState


_EXPLORATION = 1 / math.sqrt(2)


def find_deck(b: Board):
    res = { i: 4 for i in range(1, 13+1) }
    for row in b.grid:
        for e in row:
            if e != 0:
                res[e] -= 1
                assert res[e] >= 0
    return res


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
        self.mcts.root = None  # TODO: make sure this resets MCTS in the future

    def move(self, number: int):
        action = None

        # first try to reuse old MCTS calculation
        if self.mcts.root is not None:
            assert isinstance(self.mcts.root.state, CardState)
            if number in self.mcts.root.children:
                node = self.mcts.root.children[number]
                assert node.state.board.grid == self.board.grid
                action: tuple[int, int] = self.mcts.search_(node)[0]

        # if failed, create a new state
        if action is None:
            deck = find_deck(self.board)
            deck[number] -= 1  # remove current card
            math_state = MoveState(self.board, deck, number)
            action: tuple[int, int] = self.mcts.search(math_state)[0]

        assert action is not None
        self.board.make_move(action, number)

        # update the root state
        self.mcts.root = self.mcts.root.children[action]
