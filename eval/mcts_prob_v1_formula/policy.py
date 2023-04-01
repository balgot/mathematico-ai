from player import MathematicoState
from copy import deepcopy
import random


def random_policy(state: MathematicoState) -> float:
    state = deepcopy(state)
    state.deck[state.number] -= 1
    cards = [state.number] + [k for k, v in state.deck.items() for _ in range(v)]
    random.shuffle(cards)
    for i in range(30):
        if state.board.occupied_cells == 25:
            return state.board.score()
        actions = state.get_possible_actions()
        move = random.choice(actions)
        state.board.make_move(move, cards[i])
    assert False
