import os, sys
sys.path.append(os.path.join("../../"))

from copy import deepcopy
import random
import textwrap
from typing import Sequence, Union

from mathematico import Board
from src.utils.mcts2 import TreeNodeI


Deck = dict[int, int]

################################################################################
## Actions
################################################################################

CardChoice = int
MoveChoice = tuple[int, int]

################################################################################
## States
################################################################################

class CardNode(TreeNodeI):
    def __init__(
            self,
            board: Board,
            deck: Deck,
            parent: 'MoveNode | None' = None
    ) -> None:
        super().__init__(False, parent)
        self.board = board
        self.deck = deck
        self.children: dict[CardChoice, MoveNode] = {}
        self._poss_actions = [card for card in deck if deck[card] > 0]
        # order actions from most probable to least, left to right
        self._poss_actions.sort(key=lambda a: self.deck[a], reverse=True)
        self._probabs = [deck[card] for card in self._poss_actions]

    def pprint(self, move_here: 'str | MoveChoice' = "??", indent=0) -> str:
        _children = "\n".join(c.pprint(indent+1) for c in self.children.values())
        # _children = textwrap.indent(_children, "\t" + "\t" * indent)
        _mcts = super().pprint(indent + 1)
        _board = textwrap.indent(str(self.board), "\t" + "\t" * indent)
        return textwrap.indent(
            f"""
(({move_here})) {self.__class__.__name__}
    MCTS:
{_mcts}
    Board:
{_board}
    Actions:
        {self._poss_actions}
    Deck:
        {self.deck}
    Children:

{_children}
""",
            prefix="\t" * indent
        )

    def get_children(self) -> dict[CardChoice, 'MoveNode']:
        return self.children

    def get_current_player(self) -> int:
        return 0  # nature choice, no preferences

    def get_possible_actions(self) -> Sequence[CardChoice]:
        return self._poss_actions

    def take_action(self, action: CardChoice) -> 'MoveNode':
        assert action in self.deck and self.deck[action] > 0
        if action not in self.children:
            new_deck = deepcopy(self.deck)
            new_deck[action] -= 1
            self.children[action] = MoveNode(self.board, new_deck, action, self)
        return self.children[action]

    def get_reward(self) -> int:
        assert False, "card choice has never rewards"

    def expand(self) -> 'MoveNode':
        assert not self.is_fully_expanded
        assert len(self._poss_actions) > len(self.children)

        for action in self._poss_actions:
            if action not in self.children:
                node = self.take_action(action)
                if len(self._poss_actions) == len(self.children):
                    self.is_fully_expanded = True
                return node

        assert False

    def best_child(self, _exploration: float) -> 'TreeNodeI':
        action = random.choices(self._poss_actions, self._probabs, k=1)[0]
        return self.take_action(action)


class MoveNode(TreeNodeI):
    def __init__(
            self,
            board: Board,
            deck: Deck,
            card: int,
            parent: 'TreeNodeI | None' = None
    ) -> None:
        is_terminal = board.occupied_cells == 5*5
        super().__init__(is_terminal, parent)
        self.board = board
        self.deck = deck
        self.card_to_play = card
        self.children: dict[MoveChoice, CardNode] = {}
        self._poss_actions = list(board.possible_moves())
        self._next_action_idx = 0

    def pprint(self, indent=0) -> str:
        _children = "\n".join(c.pprint(m, indent+1) for m, c in self.children.items())
        _mcts = super().pprint(indent + 1)
        _board = textwrap.indent(str(self.board), "\t" + "\t" * indent)
        return textwrap.indent(
            f"""
[[{self.card_to_play}]] {self.__class__.__name__}
    MCTS:
{_mcts}
    Board:
{_board}
    Actions:
        {self._poss_actions}
    Deck:
        {self.deck}
    Children:

{_children}""",
            prefix="\t" * indent
        )

    def get_children(self) -> dict[MoveChoice, 'TreeNodeI']:
        return self.children

    def get_current_player(self) -> int:
        return 1

    def get_possible_actions(self) -> Sequence[MoveChoice]:
        return self._poss_actions

    def take_action(self, action: MoveChoice) -> CardNode:
        assert action in self._poss_actions

        if action not in self.children:
            new_board = deepcopy(self.board)
            new_board.make_move(action,self.card_to_play)
            self.children[action] = CardNode(new_board, self.deck, self)
        return self.children[action]

    def get_reward(self) -> Union[float, int]:
        return self.board.score()

    def expand(self) -> CardNode:
        assert not self.is_fully_expanded
        assert len(self._poss_actions) > len(self.children), str(self)
        assert self._next_action_idx < len(self._poss_actions)

        action = self._poss_actions[self._next_action_idx]
        self._next_action_idx += 1
        node = self.take_action(action)
        self.is_fully_expanded = self._next_action_idx >= len(self._poss_actions)
        return node

    def best_child(self, exploration: float) -> CardNode:
        assert len(self.children) > 1

        values = [child.uct(exploration) for child in self.children.values()]
        kv_pairs = zip(self.children.values(), values)
        return max(kv_pairs, key=lambda e: e[1])[0]  # deterministic
