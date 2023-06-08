"""Different Architectures for Game Mathematico."""

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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
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


class Simple_Board_v0(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.block = nn.Sequential(
            OneHot(BOARD_CARDS),
            nn.Flatten(),
            nn.Linear(5*5*14, 1024),
            nn.Sigmoid(),
            nn.Linear(1024, 1)
        )

    def forward(self, board: torch.Tensor):
        return self.block(board)


class Dense_board(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.board = nn.Sequential(
            OneHot(BOARD_CARDS),
            nn.Flatten(),
            DenseBlock([350, 1024], 0.3, True),
            DenseBlock([1024, 512, 256, 1], 0.4, False)
        )

    def forward(self, board: torch.Tensor):
        return self.board(board)


class Dense_board_v1(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.board = nn.Sequential(
            OneHot(BOARD_CARDS),
            nn.Flatten(),
            DenseBlock([350, 1024], 0.3, True),
            DenseBlock([1024, 512], 0.3, False),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

    def forward(self, board: torch.Tensor):
        return self.board(board)


class Dense_board_v2(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.board = nn.Sequential(
            OneHot(BOARD_CARDS),
            nn.Flatten(),
            DenseBlock([350, 1024, 2048, 2048, 2048], 0.3, True),
            DenseBlock([2048, 1024, 1024, 1024, 1024, 512], 0.3, False),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 1)
        )

    def forward(self, board: torch.Tensor):
        return self.board(board)


class Dense_board_v3(nn.Module):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.board = nn.Sequential(
            OneHot(BOARD_CARDS),
            nn.Flatten(),
            nn.Linear(350, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 4096),
            nn.GELU(),
            nn.Linear(4096, 2048),
            nn.GELU(),
            nn.Linear(2048, 1024),
            nn.GELU(),
            nn.Linear(1024, 512),
            nn.GELU(),
            nn.Linear(512, 256),
            nn.GELU(),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, 1)
        )

    def forward(self, board: torch.Tensor):
        return self.board(board)


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



class Amethyst(torch.nn.Module):
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

        self.mix_lines = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * (5 + 5 + 2), 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU()
        )  # combine lines

        self.out = nn.Sequential(
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        )

    def forward(self, board: torch.Tensor):
        """
        board = torch.tensor([[1,1,1,1], [1,1,1,1], ...]) -- BATCH_SIZE, 5, 5
        """

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

        # out
        out = self.out(board)
        # print(f"out shape {out.shape}")

        return out


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


################################################################################
##  LCZero inspired
################################################################################
"""Borrowed from https://github.com/yukw777/leela-zero-pytorch"""


class ConvBlock(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int,
        relu: bool = True
    ):
        super().__init__()
        assert kernel_size in (1, 3), "we only support the kernel sizes of 1 and 3"

        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            padding=1 if kernel_size == 3 else 0,
            bias=False,
        )
        self.bn = nn.BatchNorm2d(out_channels, affine=False)
        self.beta = nn.Parameter(torch.zeros(out_channels))  # type: ignore
        self.relu = relu

        # initializations
        nn.init.kaiming_normal_(self.conv.weight, mode="fan_out", nonlinearity="relu")

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x += self.beta.view(1, self.bn.num_features, 1, 1).expand_as(x)
        return F.relu(x, inplace=True) if self.relu else x


class ResBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()
        self.conv1 = ConvBlock(in_channels, out_channels, 3)
        self.conv2 = ConvBlock(out_channels, out_channels, 3, relu=False)

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)

        out += identity
        return F.relu(out, inplace=True)


class LeelaNetwork(nn.Module):
    def __init__(
        self,
        board_size: int,
        residual_channels: int,
        residual_layers: int,
    ):
        super().__init__()
        self.conv_input = ConvBlock(14, residual_channels, 3)
        self.residual_tower = nn.Sequential(
            *[
                ResBlock(residual_channels, residual_channels)
                for _ in range(residual_layers)
            ]
        )
        self.value_conv = ConvBlock(residual_channels, 1, 1)
        self.value_fc_1 = nn.Linear(board_size * board_size, 256)
        self.value_fc_2 = nn.Linear(256, 1)

    def forward(self, planes):
        planes = F.one_hot(planes.long(), 14).float()
        planes = torch.permute(planes, (0, 3, 1, 2))
        x = self.conv_input(planes)


        # residual tower
        x = self.residual_tower(x)

        # value head
        val = self.value_conv(x)
        val = F.relu(self.value_fc_1(torch.flatten(val, start_dim=1)), inplace=True)
        val = torch.tanh(self.value_fc_2(val))

        return val
