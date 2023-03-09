from mathematico import Player, Board
from ._mcts_state import MathematicoState
from mcts import mcts
class MctsPlayer(Player):
    """
    Human player takes inputs from console after printing the
    board and the next move number
    """

    def reset(self) -> None:
        self.board = Board()

    def move(self, number: int):
        print(self.board)

        state = MathematicoState(self.board, number)
        search = mcts(timeLimit = 100)
        result = search.search(initialState=state, needDetails=True)
        action = result["action"]
        
        self.board.make_move(action, number)
