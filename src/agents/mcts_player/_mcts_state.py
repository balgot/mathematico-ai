import os, sys
sys.path.append(os.path.join("../../"))

from copy import deepcopy

from mathematico import Board
from src.utils.mcts import StateI


# No need to implement Action object. An action object needs to implement
# __hash__ and __eq__, which tuple does.
CardChoice = int
MoveChoice = tuple[int, int]
"""Position on the board."""


class CardState(StateI):
    def __init__(self, board: Board, deck: dict[int, int]) -> None:
        super().__init__()
        self.board = board
        self.deck = deck
        self.children = {} # todo dict vs list
        # self._poss_actions = [k for k, v in deck.items() for _ in range(v)]
        self._poss_actions = [k for k in deck if deck[k] > 0]
        self._poss_actions.sort(key=lambda a: deck[a], reverse=True)

    def get_current_player(self) -> int:
        return 0

    def get_possible_actions(self) -> list[CardChoice]:
        # TODO: ignoring the action probability
        return self._poss_actions

    def take_action(self, action: CardChoice) -> 'MoveState':
        assert action in self.deck and self.deck[action] > 0
        if action not in self.children:
            new_deck = deepcopy(self.deck)
            new_deck[action] -= 1
            self.children[action] = MoveState(self.board, new_deck, action)
        return self.children[action]

    def is_terminal(self) -> bool:
        return False

    def get_reward(self) -> int:
        assert False, "card choice has never rewards"


class MoveState(StateI):
    def __init__(self, board: Board, deck: dict[int, int], card: int):
        self.board = board
        self.deck = deck
        self.card_to_play = card
        self.children = {}
        self._poss_actions = list(board.possible_moves())

    def get_current_player(self) -> int:
        return 1

    def get_possible_actions(self) -> list[MoveChoice]:
        return self._poss_actions

    def take_action(self, action: MoveChoice) -> 'CardState':
        if action not in self.children:
            new_board = deepcopy(self.board)
            new_board.make_move(action,self.card_to_play)
            self.children[action] = CardState(new_board, self.deck)
        return self.children[action]

    def is_terminal(self) -> bool:
        # State is terminal if all numbers are placed on board
        return self.board.occupied_cells == self.board.size ** 2

    def get_reward(self) -> int:
        return self.board.score()
