import mathematico
import pyspiel
from ._open_spiel import register_mathematico
from open_spiel.python.algorithms import mcts


register_mathematico()


def pick_uct(num_sims: int):
    # measured in /notebooks/mcts_open_spiel.ipynb
    DATA = [(5, 1.2), (10, 1.5), (20, 1.5), (60, 1.0), (100, 0.7), (200, 1.2), (500, 1.5)]
    if num_sims <= DATA[0][0]:
        return DATA[0][1]
    for (left, left_uct), (right, right_uct) in zip(DATA, DATA[1:]):
        if left <= num_sims <= right:
            return left_uct + (right_uct - left_uct) / (right - left) * (num_sims - left)
    return DATA[-1][1]


class OpenSpielPlayer(mathematico.Player):
    def __init__(self, mcts_simulations: int):
        super().__init__()
        self._game = pyspiel.load_game("mathematico")
        self.state = None
        random_eval = mcts.RandomRolloutEvaluator()
        self.bot = mcts.MCTSBot(
            self._game, uct_c=pick_uct(mcts_simulations),
            max_simulations=mcts_simulations,
            evaluator=random_eval
        )
        self.reset()

    def reset(self) -> None:
        self.state = self._game.new_initial_state()
        self.board = self.state.board

    def move(self, card_number: int) -> None:
        assert self.state.is_chance_node()
        self.state.apply_action(card_number)
        action = self.bot.step(self.state)
        self.state.apply_action(action)
