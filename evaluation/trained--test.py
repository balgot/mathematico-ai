import os, sys
sys.path.append(os.path.abspath(os.path.join("..")))
import torch

dev = torch.device("cuda")

class MyModel(torch.nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mm = torch.nn.Sequential(
            torch.nn.Flatten(),
            torch.nn.Linear(5*14, 1024),
            torch.nn.ReLU(),
            torch.nn.Dropout(),
            torch.nn.Linear(1024, 1024),
            torch.nn.ReLU(),
            torch.nn.Dropout(),
            torch.nn.Linear(1024, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, 1)
        )

    def forward(self, b):
        one_hot = torch.nn.functional.one_hot(b.long(), 14)
        return self.mm(one_hot.float())

line_model = MyModel().to(dev)

class CombineModel(torch.nn.Module):
    def __init__(self, line_prep, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_prep = line_prep
        self.out = torch.nn.Sequential(
            torch.nn.Linear(5 + 5 + 1 + 1 + 25, 1024),
            torch.nn.ReLU(),
            torch.nn.Dropout(),
            torch.nn.Linear(1024, 1024),
            torch.nn.ReLU(),
            torch.nn.Linear(1024, 1)
        )

    def forward(self, board: torch.Tensor):
        mask = (board == 0).float()
        mask = torch.flatten(mask, start_dim=1)

        # rows of the board
        rows = []
        for i in range(5):
            row = board[:, i, :]
            rows.append(self.line_prep(row))

        # cols of the board
        cols = []
        trans = board.transpose(-1, -2)
        for i in range(5):
            col = trans[:, i, :]
            cols.append(self.line_prep(col))

        # main/anti diagonal
        main = board.diagonal(0, -2, -1)[:, :]
        anti = torch.flip(board, [-2, -1]).diagonal(0, -2, -1)[:, :]
        main = self.line_prep(main)
        anti = self.line_prep(anti)

        catted = torch.cat([*rows, *cols, main, anti, mask], dim=-1)
        return self.out(catted)


model = CombineModel(line_model).to(dev)
model.load_state_dict(torch.load("trained_o4299lc5.pt"))
print("loaded...")

from src.agents.mcts_player import MctsPlayer

def policy_static(state) -> float:
    board = torch.tensor([state.board.grid], device=dev)
    return model(board)

class MCTS__100ms(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=100, policy=policy_static)

class MCTS__1s(MctsPlayer):
    def __init__(self):
        super().__init__(max_time_ms=1_000, policy=policy_static)
