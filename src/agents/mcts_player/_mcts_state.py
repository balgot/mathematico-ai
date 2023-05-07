import os, sys
sys.path.append(os.path.abspath(os.path.join("../../")))

from copy import deepcopy
from typing import Tuple, Dict, List

from mathematico import Board
from src.utils.mcts import StateI


# No need to implement Action object. An action object needs to implement
# __hash__ and __eq__, which tuple does.
CardChoice = int
MoveChoice = Tuple[int, int]
"""Position on the board."""


class CardState(StateI):
    def __init__(self, board: Board, deck: Dict[int, int]) -> None:
        super().__init__()
        self.board = board
        self.deck = deck
        self.children = {} # todo dict vs list
        # self._poss_actions = [(k, i) for k, v in deck.items() for i in range(v)]
        self._poss_actions = [k for k in deck if deck[k] > 0]
        # self._poss_actions.sort(key=lambda a: deck[a], reverse=True)

    def get_current_player(self) -> int:
        return 0

    def get_possible_actions(self) -> List[CardChoice]:
        return self._poss_actions

    def take_action(self, action: CardChoice) -> 'MoveState':
        card = action
        assert card in self.deck and self.deck[card] > 0
        if action not in self.children:
            new_deck = deepcopy(self.deck)
            new_deck[card] -= 1
            self.children[action] = MoveState(self.board, new_deck, card, self.deck[card])
        return self.children[action]

    def is_terminal(self) -> bool:
        return False

    def get_reward(self) -> int:
        assert False, "card choice has never rewards"


class MoveState(StateI):
    def __init__(self, board: Board, deck: Dict[int, int], card: int, cnt: int = 1):
        self.board = board
        self.deck = deck
        self.card_to_play = card
        self.children = {}
        self._poss_actions = list(board.possible_moves())
        self.cnt = cnt

    def get_cnt(self):
        return self.cnt

    def get_current_player(self) -> int:
        return 1

    def get_possible_actions(self) -> List[MoveChoice]:
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
