import os, sys
sys.path.append(os.path.abspath(os.path.join("../")))
from typing import Tuple, Sequence, List, Union, Callable, Optional
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


class _MctsPlayer(mathematico.Player):
    # TODO: might not work if MathematicoState is defined otherwise, depends
    # on the full representation of the game in the each node

    # TODO: does not expect playing other moves than the ones obtained
    # by the self.best_move (setting up the board should work)

    # TODO: requires editting MCTS to be able to setup the root, see also
    # some methods below <*>

    def __init__(self,
            max_time: Union[int, float, Callable[[int], int], None],
            max_iters: Union[int, float, Callable[[int], int], None],
            policy: Callable[[MathematicoState], float],
            exploration: Union[float, Callable[[int], float]] = 1 / (2 ** .5),
    ):
        """
        Create an MCTS player.

        Arguments
        =========
            max_time: if a number, then it is a maximum time per
                one move selection [in miliseconds]; if callable,
                then it gets as the input the number of occupied
                cells on the board and should return the max time
            max_iters: if a number, then maximum number of MCTS
                simulations to run per one move selection; if
                callable, then mapping from number of occupied cells
                to max number of simulations
            policy: function to use in the rollout phase, mapping
                game state to the EXPECTED return from this state
        """
        super().__init__()
        self._max_time = max_time
        if isinstance(max_time, (float, int, type(None))):
            self._max_time = lambda _iter: max_time
        self._max_iters = max_iters
        if isinstance(max_iters, (float, int, type(None))):
            self._max_iters = lambda _iter: max_iters
        self._exp = exploration
        if isinstance(exploration, float):
            self._exp = lambda _iter: exploration
        self._policy = policy

        # for caching MCTS trees across moves
        self._mcts: Optional[mcts.MCTS] = None
        self._root: Optional[MathematicoState] = None  # <*>

    def reset(self) -> None:
        self.board = Board()
        self._mcts = None
        self._root = None

    def best_move(self, number):
        if self._mcts is None: # <*>
            state = MathematicoState(self.board, number)
        else:
            assert self._root is not None
            state = self._root

        max_time = self._max_time(self.board.occupied_cells)
        max_iter = self._max_iters(self.board.occupied_cells)
        exp = self._exp(self.board.occupied_cells)

        self._mcts = mcts.MCTS(
            time_limit=max_time,
            iters_limit=max_iter,
            exploration_const=exp,
            rollout_policy=self._policy
        )

        # <*>
        # <*>

        # TODO: if stochastic, edit here
        action, value = self._mcts.search(state)[0]
        return action, value

    def play_move(self, move, number):
        self.board.make_move(move, number)
        assert self._mcts is not None
        root = self._mcts.root
        assert root is not None
        next_mcts_root = root.children[move]
        # maybe check that boards are the same?
        # <*>
        # <*>

    def move(self, number: int):
        action, value = self.best_move(number)
        # print(f"[info] Expecting value: {value}\tFor action: {action}")
        self.play_move(action, number)