import torch
import torch.nn as nn
import torch.nn.functional as F
import math


BOARD_SIZE = 5
AVAILABLE_CARDS = 13
BOARD_CARDS = AVAILABLE_CARDS + 1  # for no card


################################################################################
##  Input Processing
################################################################################

class OneHot(nn.Module):
    def __init__(self, num_classes, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.num_classes = num_classes

    def forward(self, x: torch.tensor) -> torch.tensor:
        """
        Expecting input of shape: [BATCH_SIZE, *] of type int
        Returns: [BATCH_SIZE, *, self.num_classes]
        """
        res = F.one_hot(x.long(), num_classes=self.num_classes).float()
        return res


################################################################################
##  Blocks
################################################################################

class Dense(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.fc = nn.Linear(*args, **kwargs)
        self.activation = nn.ReLU()

    def forward(self, x: torch.Tensor):
        return self.activation(self.fc(x))


class DenseBlock(nn.Module):
    def __init__(self, sizes: list, dropout: float, use_norm: bool) -> None:
        super().__init__()
        layers = []
        for ins, out in zip(sizes, sizes[1:]):
            layers.append(nn.Sequential(
                nn.Linear(in_features=ins, out_features=out),
                nn.ReLU(),
                nn.Dropout1d(dropout)
            ))

        if use_norm:
            layers.append(nn.LayerNorm(sizes[-1]))
        self.block = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor):
        res = self.block(x)
        return res


################################################################################
##  Models
################################################################################


class NonConvDenseOnly_v1(nn.Module):
    """
    Just FF NN, works with flattened one-hot encoded game.
    """
    def __init__(self,  *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.board_prep = nn.Sequential(
            OneHot(BOARD_CARDS),
            nn.Flatten(start_dim=1), # gives 5*5*14=350
            DenseBlock([350, 512, 1024, 2048], 0.3, True),
            DenseBlock([2048, 1024, 512, 256], 0.5, True)
        )
        self.card_prep = nn.Sequential(
            OneHot(BOARD_CARDS),
            nn.Flatten(start_dim=1),  # 14
            DenseBlock([14, 64, 128, 256], 0, True)
        )
        self.final = nn.Sequential(
            DenseBlock([256 + 256, 1024, 2048], 0.1, True),
            DenseBlock([2048, 1024, 512], 0.1, True),
            DenseBlock([512, 256, 128, 64, 32, 16, 1], 0, False),
        )

    def forward(self, board: torch.Tensor, card: torch.Tensor):
        board = self.board_prep(board)
        card = self.card_prep(card)
        joined = torch.cat([board, card], dim=-1)
        return self.final(joined)


class NNv1(torch.nn.Module):
    def __init__(self):
        super().__init__()

        self.features = nn.Conv2d(in_channels=BOARD_CARDS, out_channels=16, kernel_size=(5, 1), padding=0)  # feature extractor
        self.line_proc = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU()
        )  # line processor


        self.card_proc = nn.Sequential(
            nn.Linear(AVAILABLE_CARDS, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Flatten(start_dim=1)
        )  # card block

        self.mix_lines = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * (5 + 5 + 2), 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU()
        )  # combine lines

        self.out = nn.Sequential(
            nn.Linear(128 + 128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )  # card-board mix

    def forward(self, board: torch.Tensor, card: torch.Tensor):
        """
        board = torch.tensor([[1,1,1,1], [1,1,1,1], ...]) -- BATCH_SIZE, 5, 5
        card = torch.tensor(card) -- BATCH_SIZE
        """

        # Analysing the current card
        card = F.one_hot(card.long() - 1, num_classes=AVAILABLE_CARDS).float()
        card = self.card_proc(card)

        # The board features
        board = F.one_hot(board.long(), num_classes=BOARD_CARDS).float()
        board = board.permute(0, 3, 1, 2) # permute dimensions to match expected order
        # print(f"permuted board shape = {board.shape}")

        # rows of the board
        rows = self.features(board)
        # print(f"rows shape = {rows.shape}")

        # cols of the board
        cols = self.features(board.transpose(-1, -2)) # TODO: makes sence?
        # print(f"cols shape = {cols.shape}")

        # main/anti diagonal
        main = board.diagonal(0, -2, -1)[:, :, :, None]
        anti = torch.flip(board, [-2, -1]).diagonal(0, -2, -1)[:, :, :, None]
        # print(f"*diag shape {main.shape}")
        # print(f"*anti shape {anti.shape}")
        main = self.features(main)
        anti = self.features(anti)
        # print(f"diag shape {main.shape}")
        # print(f"anti shape {anti.shape}")

        # combine the features
        combined = []
        for tensor in (rows, cols, main, anti):
            spl = torch.split(tensor, 1, dim=3)
            for t in spl:
                t = t.squeeze(dim=3)
                t = t.permute(0, 2, 1)
                t = self.line_proc(t)
                t = t.permute(0, 2, 1)
                combined.append(t)

        board = torch.cat(combined, dim=-1)
        # print(f"cat shape {board.shape}")
        board = self.mix_lines(board)
        # print(f"mixed lines shape {board.shape}")

        # combine
        comb = torch.cat([board, card], dim=-1)
        # print(f"combined {comb.shape}")

        # out
        out = self.out(comb)
        # print(f"out shape {out.shape}")

        return out