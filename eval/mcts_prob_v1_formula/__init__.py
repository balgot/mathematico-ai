from policy import random_policy
from player import MctsPlayer


class MCTSPlayer_prob_v0__100ms(MctsPlayer):
    def __init__(self):
        super().__init__(max_time=100, policy=random_policy)


class MCTSPlayer_prob_v0__500ms(MctsPlayer):
    def __init__(self):
        super().__init__(max_time=500, policy=random_policy)


class MCTSPlayer_prob_v0__1sec(MctsPlayer):
    def __init__(self):
        super().__init__(max_time=1_000, policy=random_policy)


class MCTSPlayer_prob_v0__10sec(MctsPlayer):
    def __init__(self):
        super().__init__(max_time=10_000, policy=random_policy)
