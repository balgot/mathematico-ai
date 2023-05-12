import torch
import torch.nn as nn
import torch.nn.functional as F



class ConvBlock(nn.Module):
    def __init__(
            self, in_channels: int, out_channels: int, kernel_size: int, relu: bool = True
        ):
        super().__init__()
        # we only support the kernel sizes of 1 and 3
        assert kernel_size in (1, 3)

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
        # print(f"\t\t[conv-in] {x.shape=}")
        x = self.conv(x)
        # print(f"\t\t[conv] {x.shape=}")
        x = self.bn(x)
        # print(f"\t\t[norm] {x.shape=}")
        x += self.beta.view(1, self.bn.num_features, 1, 1).expand_as(x)
        # print(f"\t\t[+beta] {x.shape=}")
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
        # first conv layer
        # print(f"[input] {planes.shape=}")
        planes = F.one_hot(planes.long(), 14).float()
        # print(f"[one-hot] {planes.shape=}")
        planes = torch.permute(planes, (0, 3, 1, 2))
        # print(f"[permute] {planes.shape=}")
        x = self.conv_input(planes)
        # print(f"[conv1] {x.shape=}")


        # residual tower
        x = self.residual_tower(x)
        # print(f"[tower] {x.shape=}")

        # value head
        val = self.value_conv(x)
        val = F.relu(self.value_fc_1(torch.flatten(val, start_dim=1)), inplace=True)
        val = torch.tanh(self.value_fc_2(val))

        return val
