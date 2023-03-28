import os, sys
sys.path.append(os.path.abspath(os.path.join("../")))
from typing import Tuple, Sequence, List
from copy import deepcopy
import mathematico
from mathematico import Board
from random import randrange
from collections import Counter
from src.utils import mcts



# The action type (row and col to play)
Action = Tuple[int, int]

# The card we are supposed to place on the board
Card = int

# For representing the available cards, card ↦ number of cards in the deck
Deck = dict[Card, int]


class MathematicoState(mcts.StateI):
    """
    State of the game, represented by the positions
    of the cards already placed on the board and the card
    to place.
    """

    def __init__(self, board: Board, number: Card, cards_left: 'Deck | None' = None):
        self.board: Board = board
        self.number: Card = number
        self.deck = cards_left

        # count the number of cards available
        if self.deck is None:
            self.deck = {i: 4 for i in range(1, 14)}
            for row in range(board.size):
                for col in range(board.size):
                    num = board.grid[row][col]
                    if num != 0:
                        assert num in self.deck, f"{num=} {row=} {col=} {board=}"
                        self.deck[num] -= 1
                        if not self.deck[num]:
                            self.deck.pop(num)
        
        assert number in self.deck, f"{number=} {cards_left=}"

    def get_possible_actions(self) -> Sequence[Action]:
        return list(self.board.possible_moves())

    def take_action(self, action: Action) -> 'list[tuple[mcts.StateI, float]]':
        cnt = sum(self.deck.values()) - 1  # one card is eliminated anyways
        res = []

        # find all possible states after playing card: self.number at position action
        for card, n in self.deck.items():
            if card == self.number and n == 1:
                continue
            board = deepcopy(self.board)
            board.make_move(action, self.number)  # take action that leads TO this state
            deck = deepcopy(self.deck) # .copy()  # enough for int ↦ int
            deck[self.number] -= 1
            if not deck[self.number]:
                deck.pop(self.number)
            res.append((MathematicoState(board, card, deck), n / cnt))
        return res

    def is_terminal(self) -> bool:
        return self.board.occupied_cells == self.board.size ** 2

    def get_reward(self):
        return self.board.score()



class MctsPlayer(mathematico.Player):
    def __init__(self, max_time, max_iters, policy):
        super().__init__()
        self._mcts = mcts.MCTS(time_limit=max_time, iters_limit=max_iters, rollout_policy=policy)
    
    def reset(self) -> None:
        self.board = Board()

    def best_move(self, number):
        state = MathematicoState(self.board, number)
        action, value = self._mcts.search(state)[0]
        return action, value

    def play_move(self, move, number):
        self.board.make_move(move, number)

    def move(self, number: int):
        action, value = self.best_move(number)
        # print(f"[info] Expecting value: {value}\tFor action: {action}")        
        self.play_move(action, number)