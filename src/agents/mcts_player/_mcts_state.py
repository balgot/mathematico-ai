import os, sys
sys.path.append(os.path.join("../../"))

from copy import deepcopy
from random import randrange

from mathematico import Board
from src.utils.mcts import StateI


# No need to implement Action object. An action object needs to implement
# __hash__ and __eq__, which tuple does.
Action = tuple[int, int]
"""Position on the board."""


class MathematicoState(StateI):
    def __init__(self, board: Board, card: int):
        self.board: Board = board
        self.card: int = card
        deck = {i: 4 for i in range(1, 13+1)}
        for i in range(self.board.size):
            for j in range(self.board.size):
                current_card = self.board.grid[i][j]
                if current_card != 0:
                    deck[current_card] -= 1
        deck[card] -= 1
        self.numbers_left = [card
                    for card, count in deck.items()
                    for _  in range(count)]

    def get_current_player(self) -> int:
        return 1

    def get_possible_actions(self) -> list[Action]:
        return list(self.board.possible_moves())

    def take_action(self, action: Action) -> 'MathematicoState':
        next_state = deepcopy(self)
        next_state.board.make_move(action, next_state.card)
        # pick a random card as next
        card_idx = randrange(len(next_state.numbers_left))
        next_state.card = next_state.numbers_left.pop(card_idx)
        return next_state

    def is_terminal(self) -> bool:
        # State is terminal if all numbers are placed on board
        return self.board.occupied_cells == self.board.size ** 2

    def get_reward(self) -> int:
        return self.board.score()
