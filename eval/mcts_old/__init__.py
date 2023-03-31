from _mcts_player import MctsPlayer


class MctsPlayer__100_ms(MctsPlayer):
    def __init__(self):
        super().__init__(100)


class MctsPlayer__1s(MctsPlayer):
    def __init__(self):
        super().__init__(1_000)


class MctsPlayer__10s(MctsPlayer):
    def __init__(self):
        super().__init__(10_000)


class MctsPlayer__30s(MctsPlayer):
    def __init__(self):
        super().__init__(30_000)
