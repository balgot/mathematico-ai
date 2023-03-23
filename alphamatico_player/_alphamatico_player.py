from ._mcts_state import MathematicoState
from libs.mathematico.game import Player, Board
from libs.MCTS.mcts import mcts

import tensorflow as tf
import math



class ValueNetwork():
    def __init__(self, model=None, model_path=None):
        if model:
            self.model = model
        
        elif model_path:
            self.model = tf.keras.models.load_model(model_path)
        
        else:
            model = self.newModel() 
        return 
    
    
    def newModel(self):
        #TODO: This should create a new model
        raise NotImplementedError
    
    def evalState(self, state: MathematicoState):
        # TODO: This should return the models evaluation of the state
        # Do not add arguments as this will be used as rollout policy
        raise NotImplementedError
    

class AlphamaticoPlayer(Player):
    """
    Human player takes inputs from console after printing the
    board and the next move number
    """

    def __init__(self, timeLimit=10, explorationConstant=1 / math.sqrt(2), model = None, model_path = None):
        super().__init__()
        self.model = ValueNetwork(model=model, model_path=model_path)
        
        self.mcts = mcts(timeLimit=timeLimit, explorationConstant=explorationConstant, rolloutPolicy=self.model.evalState)
    
    def reset(self) -> None:
        self.board = Board()

    def move(self, number: int):
        state = MathematicoState(self.board, number)
        result = self.mcts.search(initialState=state, needDetails=True)
        action = result["action"]
        
        self.board.make_move(action, number)
