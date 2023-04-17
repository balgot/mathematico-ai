"""Extracting data from MCTS search tree."""
import os, sys
sys.path.append(os.path.abspath(os.path.join("../..")))

from src.utils.mcts import _TreeNode as TreeNode
from src.agents.mcts_player import CardState, MoveState
from copy import deepcopy


Board = list[list[int]]
Expected = float
Visits = int
Depth = int  # how far from the root of MCTS
Height = int  # how far until full board
Stats = tuple[Board, Expected, Visits, Depth, Height]


def _reward(node: TreeNode):
    assert node.num_visits > 0
    return node.total_reward / node.num_visits


def _extract_rec(root: TreeNode, result: list[Stats], depth=0):
    if root.num_visits == 0:
        return

    state: 'CardState | MoveState' = root.state
    _board = deepcopy(state.board.grid)
    _exp = _reward(root)
    _vis = root.num_visits
    _dep = depth
    _hei = 25 - state.board.occupied_cells
    result.append((_board, _exp, _vis, _dep, _hei))

    for child in root.children.values():
        _extract_rec(child, result, depth + 1)


def extract(root: TreeNode) -> list[Stats]:
    """Traverse the tree and gather all info."""
    result = []
    _extract_rec(root, result)
    return result
