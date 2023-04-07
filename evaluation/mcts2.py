import os, sys
sys.path.append(os.path.abspath(os.path.join("..")))

from src.agents.mcts_player.player2 import MctsPlayer


class MCTS__100ms(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=100)


class MCTS__1s(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=1_000)


class MCTS__10s(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=10_000)


class MCTS__30s(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=30_000)


if __name__ == "__main__":
    try:
        from mathematico import Mathematico
        game = Mathematico()
        player = MCTS__100ms()
        game.add_player(player)
        game.play(verbose=True)
    except Exception as e:
        import sys
        exc_type, exc_value, tb = sys.exc_info()
        if tb is not None:
            prev = tb
            curr = tb.tb_next
            while curr is not None:
                prev = curr
                curr = curr.tb_next
            print("Trace\n======")
            for k, v in prev.tb_frame.f_locals.items():
                print(f"{k} = {v}")
            print("\n\n")
        raise e
