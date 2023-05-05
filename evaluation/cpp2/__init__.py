import os, sys
sys.path.append(os.path.dirname(__file__))
from agent import Cpp2Player


class Cpp__100ms(Cpp2Player):
    def __init__(self):
        super().__init__(100, None)

class Cpp__500ms(Cpp2Player):
    def __init__(self):
        super().__init__(500, None)

class Cpp__1000ms(Cpp2Player):
    def __init__(self):
        super().__init__(1000, None)
