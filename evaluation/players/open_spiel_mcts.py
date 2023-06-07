import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from src.agents.ospiel import OpenSpielPlayer


class OpenSpiel__10(OpenSpielPlayer):
    def __init__(self):
        super().__init__(10)

class OpenSpiel__20(OpenSpielPlayer):
    def __init__(self):
        super().__init__(20)

class OpenSpiel__50(OpenSpielPlayer):
    def __init__(self):
        super().__init__(50)

class OpenSpiel__100(OpenSpielPlayer):
    def __init__(self):
        super().__init__(100)

class OpenSpiel__250(OpenSpielPlayer):
    def __init__(self):
        super().__init__(250)

class OpenSpiel__500(OpenSpielPlayer):
    def __init__(self):
        super().__init__(500)

class OpenSpiel__1000(OpenSpielPlayer):
    def __init__(self):
        super().__init__(1000)


if __name__ == "__main__":
    from mathematico import Mathematico
    game = Mathematico()
    player = OpenSpiel__250()
    game.add_player(player)
    game.play(verbose=True)
    print(player.board.score())
