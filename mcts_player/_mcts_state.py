from typing import Tuple, Iterator, List
from copy import deepcopy
from libs.mathematico import Board
from random import randrange, random
from numpy import concatenate
Action = Tuple[int, int]

class MathematicoState():
    def __init__(self, board, number):
        self.board: Board = board
        self.number: int = number
        self.numbers_left: List[int] = [i for i in range(1, 14) for _ in range(4)]
        self.numbers_left.remove(number)
    
    def getCurrentPlayer(self):
        # 1 for maximiser, -1 for minimiser
        return 1

    def getPossibleActions(self) -> Iterator[Action]:
        return self.board.possible_moves()

    def takeAction(self, action: Action):
        newState = deepcopy(self)
        newState.board.make_move(action, newState.number)
        # pick a random card as next 
        newState.number = newState.numbers_left.pop(randrange(len(newState.numbers_left)))
        return newState
    
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