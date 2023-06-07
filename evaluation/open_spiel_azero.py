from azero import load_trained_bot as _load_azero_bot
import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.agents.ospiel import OpenSpielPlayer

PATH = os.path.join(os.path.dirname(__file__), "azero-logs/")
CHECKPOINT = -1

def load_trained_bot():
    with open(os.path.join(PATH, "config.json"), "r") as f:
        cfg = json.load(f)

    bot, _ = _load_azero_bot(cfg, PATH, CHECKPOINT, is_eval=True)
    return bot

class MLP_1024x6(OpenSpielPlayer):
    def __init__(self):
        super().__init__(1)
        self.bot = load_trained_bot()


if __name__ == "__main__":
    import mathematico
    g = mathematico.Mathematico()
    g.add_player(MLP_1024x6())
    g.play(verbose=True)
