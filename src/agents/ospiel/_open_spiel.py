"""Porting Mathematico to open_spiel."""
import pyspiel
import mathematico
import numpy as np


_GAME_TYPE = pyspiel.GameType(
    short_name="mathematico",
    long_name="Mathematico",

    dynamics=pyspiel.GameType.Dynamics.SEQUENTIAL,
    chance_mode=pyspiel.GameType.ChanceMode.EXPLICIT_STOCHASTIC,
    information=pyspiel.GameType.Information.PERFECT_INFORMATION,
    utility=pyspiel.GameType.Utility.GENERAL_SUM,
    reward_model=pyspiel.GameType.RewardModel.TERMINAL,

    max_num_players=1,
    min_num_players=1,
    provides_information_state_string=True,
    provides_information_state_tensor=True,
    provides_observation_string=True,
    provides_observation_tensor=True,
    provides_factored_observation_string=True
)

_GAME_INFO = pyspiel.GameInfo(
    num_distinct_actions=25,
    max_chance_outcomes=13,
    num_players=1,
    min_utility=0,
    max_utility=1000,
    max_game_length=25
)

class _MathematicoGame(pyspiel.Game):
    def __init__(self, params=None):
        super().__init__(_GAME_TYPE, _GAME_INFO, params or dict())

    def new_initial_state(self):
        """Returns a state corresponding to the start of a game."""
        return _MathematicoState(self)

    def make_py_observer(self, iig_obs_type=None, params=None):
        """Returns an object used for observing game state."""
        _iig = iig_obs_type or pyspiel.IIGObservationType(perfect_recall=False)
        return _MathematicoOverserver(_iig, params)


class _MathematicoState(pyspiel.State):
    def __init__(self, game):
        """Constructor; should only be called by Game.new_initial_state."""
        super().__init__(game)
        self.board = mathematico.Board()
        self.deck = {k: 4 for k in range(1, 1+13)}
        self.card = None
        self._game_over = False
        self._next_player = 0

    def current_player(self):
        """Returns id of the next player to move, or TERMINAL if game is over."""
        if self._game_over:
            return pyspiel.PlayerId.TERMINAL
        if self.card is None:
            return pyspiel.PlayerId.CHANCE
        return self._next_player

    def _legal_actions(self, player):
        """Returns a list of legal actions, sorted in ascending order."""
        assert player >= 0
        return [5*row + col for row, col in self.board.possible_moves()]

    def chance_outcomes(self):
        """Returns the possible chance outcomes and their probabilities."""
        assert self.is_chance_node()
        assert self.card is None
        cards_left = 13*4 - self.board.occupied_cells
        return [(k, v / cards_left) for k, v in self.deck.items() if v > 0]

    def _apply_action(self, action):
        """Applies the specified action to the state."""
        if self.is_chance_node():
            self.card = action
            assert self.deck[action] > 0
            self.deck[action] -= 1
        else:
            self.board.make_move(divmod(action, 5), self.card)
            self.card = None
            if self.board.occupied_cells == 25:
                self._game_over = True

    def _action_to_string(self, player, action):
        """Action -> string."""
        if player == pyspiel.PlayerId.CHANCE:
            return f"Card:{action}"
        else:
            return f"Move:{action}"

    def is_terminal(self):
        """Returns True if the game is over."""
        return self._game_over

    def returns(self):
        """Total reward for each player over the course of the game so far."""
        if not self._game_over:
            return [0]
        return [self.board.score()]

    def __str__(self):
        """String for debug purposes. No particular semantics are required."""
        return f"{self.board}\nCard: {self.card}\nDeck: {self.deck}"


class _MathematicoOverserver:
    def __init__(self, iig_obs_type, params):
        """Initializes an empty observation tensor."""
        if params:
            raise ValueError(f"Observation parameters not supported; passed {params}")
        self.tensor = np.zeros(14 * 25 + 14)
        self.dict = {
            "board": self.tensor[: 14*25],
            "card": self.tensor[14*25 :]
        }

    def one_hot(self, x):
        return np.identity(14)[x].flatten()

    def set_from(self, state, player):
        """Updates `tensor` and `dict` to reflect `state` from PoV of `player`."""
        self.tensor.fill(0)
        self.dict["board"] = self.one_hot(np.array(state.board.grid).flatten())
        if state.card is not None:
            self.dict["card"] = self.one_hot([state.card])

    def string_from(self, state, player):
        """Observation of `state` from the PoV of `player`, as a string."""
        return str(state)


def register_mathematico():
    pyspiel.register_game(_GAME_TYPE, _MathematicoGame)


if __name__ == "__main__":
    register_mathematico()
    game = pyspiel.load_game("mathematico")
    state = game.new_initial_state()
    while not state.is_terminal():
        action = np.random.choice(state.legal_actions())
        state.apply_action(action)
    print(state)
    print("Score =", state.returns()[0])
