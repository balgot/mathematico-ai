from libs.mathematico.game import Player, Board
from ._mcts_state import MathematicoState
from libs.MCTS.mcts import mcts
import math

class MctsPlayer(Player):
    """
    Human player takes inputs from console after printing the
    board and the next move number
    """

    def __init__(self, timeLimit=10, explorationConstant=1 / math.sqrt(2)):
        super().__init__()
        self.mcts = mcts(timeLimit=timeLimit, explorationConstant=explorationConstant)
    
    def reset(self) -> None:
        self.board = Board()

    def move(self, number: int):
        state = MathematicoState(self.board, number)
        result = self.mcts.search(initialState=state, needDetails=True)
        action = result["action"]
        
        self.board.make_move(action, number)
