from typing import Tuple, Iterator, List
from copy import deepcopy
from libs.mathematico import Board
from random import randrange, random
from numpy import concatenate
Action = Tuple[int, int]

class MathematicoDecesionState():
    # Dont have the init like MathematicoGenerateState to avoid problem with type references
    def __init__(self, board, number, numbers_left): 
        self.board: Board = board
        self.number: int = number
        self.numbers_left: List[int] = numbers_left
        
    def __init__(self, board, number, numbers_left=None): 
        self.board: Board = board
        self.number: int = number
        if numbers_left:
            self.numbers_left=numbers_left
        else:
            self.numbers_left: List[int] = [i for i in range(1, 14) for _ in range(4)]
            self.numbers_left.remove(number)
        
    def getCurrentPlayer(self):
        # 1 for maximiser, -1 for minimiser
        return 1

    def getPossibleActions(self) -> Iterator[Action]:
        return self.board.possible_moves()

    def takeAction(self, action: Action):
        new_board = deepcopy(self.board)
        new_numbers_left = deepcopy(self.numbers_left)
        new_board.make_move(action, self.number)
        return MathematicoGenerateState(new_board, new_numbers_left)
    
    def isTerminal(self):
        # State is terminal if all numbers are placed on board
        return self.board.occupied_cells == self.board.size ** 2

    def getReward(self):
        return self.board.score()
            

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.board.grid == other.board.grid and \
            self.number == other.number


    def toVector(self):
        return concatenate(self.board.grid) + [self.number]
# No need to implement Action object. An action object needs to implement
# __hash__ and __eq__, which tuple does.


class MathematicoGenerateState():
    def __init__(self, board, numbers_left):
        self.board: Board = board
        self.number: int = 0
        self.numbers_left = numbers_left
    
    
    def getCurrentPlayer(self):
        # 1 for maximiser, -1 for minimiserself.board.score()self.board.score()
        return self.board.score()

    def getPossibleActions(self) -> Iterator[Action]:
        return [(-1,-1)]

    def takeAction(self, _: Action):
        new_number = self.numbers_left.pop(randrange(len(self.numbers_left)))
        return MathematicoDecesionState(self.board, new_number, self.numbers_left)
    
    def isTerminal(self):
        # State is terminal if all numbers are placed on board
        return self.board.occupied_cells == self.board.size ** 2

    def getReward(self):
        return self.board.score()
            

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
            self.board.grid == other.board.grid and \
            self.number == other.number


    def toVector(self):
        return concatenate(self.board.grid) + [self.number]