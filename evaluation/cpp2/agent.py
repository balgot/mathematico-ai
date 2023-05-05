from mathematico import Player, Board

try:
    import _cpp_mcts as cpp  # noqa # type: ignore
except ImportError as e:
    raise RuntimeError(
        "C++ compiled library not found. Did you forget to run `make lib`?"
    ) from e


class Cpp2Player(Player):
    def __init__(self, max_time_per_move__ms, max_simlus_per_move, exploration=0.707106781):
        super().__init__()
        self.max_time = max_time_per_move__ms
        self.max_runs = max_simlus_per_move
        self.exp = exploration

    def reset(self) -> None:
        self.board = Board()

    def move(self, card_number: int, verbose=False) -> None:
        move, simuls = cpp.mcts(
            self.board.grid,
            card_number,
            self.max_time
        )
        if verbose:
            print(f"{move=}\t\t{simuls=}")
        self.board.make_move(move, card_number)
