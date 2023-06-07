import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.agents.mcts_player import MctsPlayer


class MCTS__10(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=None, max_simulations=10)


class MCTS__20(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=None, max_simulations=20)


class MCTS__50(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=None, max_simulations=50)


class MCTS__100(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=None, max_simulations=100)


class MCTS__250(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=None, max_simulations=250)


class MCTS__500(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=None, max_simulations=500)


if __name__ == "__main__":
    from mathematico import Mathematico
    game = Mathematico()
    player = MCTS__10()
    game.add_player(player)
    game.play(verbose=True)
