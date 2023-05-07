"""Find all symetries of the board."""
from copy import deepcopy
from typing import List, Tuple


# This is how the board is represented internally
Board2D = List[List[int]]


def _spec_swap(board: Board2D, i: int, j: int) -> Board2D:
    """
    Special swap operation.

    Swap rows and cols to change the inner and outer
    cells of the board.

    Arguments
    =========
        board: the board to find the symmetries of
        i: the first index that determines swapping
        j: second index taht determines swapping

    Returns
    =======
        augmented (deepcopy) of the board

    Notes
    =====
        If `i == j` than this operator acts as the identity.
    """
    board = deepcopy(board)
    board[i], board[j] = board[j], board[i]
    for k in range(5):
        board[k][i], board[k][j] = board[k][j], board[k][i]
        board[k][4-i], board[k][4-j] = board[k][4-j], board[k][4-i]
    board[4-i], board[4-j] = board[4-j], board[4-i]
    return board

def _vertical(board: Board2D) -> Board2D:
    """
    Vertical symmetry.

    Flip the board vertically around the 2nd (the middle) column.

    Arguments
    =========
        board: the board to find the symmetries of

    Returns
    =======
        augmented (deepcopy) of the board
    """
    board = deepcopy(board)
    return [row[::-1] for row in board]

def _horizontal(board: Board2D) -> Board2D:
    """
    Horizontal symmetry.

    Flip the board horizontally around the 2nd (the middle) row.

    Arguments
    =========
        board: the board to find the symmetries of

    Returns
    =======
        augmented (deepcopy) of the board
    """
    board = deepcopy(board)
    return board[::-1]

def _trans(board: Board2D) -> None:
    """
    Transpose the board, in place.

    Arguments
    =========
        board: the board of the game mathematico

    Returns
    =======
        nothing, performs the operation in place
    """
    for i in range(5):
        for j in range(i):
            board[i][j], board[j][i] = board[j][i], board[i][j]

def _rotate(board: Board2D) -> Board2D:
    """
    Rotate the board once, clockwise by 90deg.

    Arguments
    =========
        board: the board to find the symmetries of

    Returns
    =======
        augmented (deepcopy) of the board
    """
    board = _horizontal(board)
    _trans(board)
    return board

def all_symmetries(board: Board2D) -> List[Board2D]:
    """
    Find all symmetries of the board.

    Find and filter out all unique symmetries of the board.

    Arguments
    =========
        board: the Mathematico board

    Returns
    =======
        list of (copies), unique boards that are equivalent
        to @board in the sense that they give the same score
    """
    assert len(board) == 5
    assert all(len(row) == 5 for row in board)

    board = deepcopy(board)
    result = []

    for i, j in [(0, 0), (0, 1), (0, 3), (0, 4), (1, 3), (1, 4), (3, 4)]:
        b = _spec_swap(board, i, j)
        for _rot in range(4):
            result.append(deepcopy(b))
            result.append(_vertical(b))
            result.append(_horizontal(b))
            b = _rotate(b)

    # filter out the different boards
    result.sort()
    res = []
    for r in result:
        if not res or res[-1] != r:
            res.append(r)

    return res


def move_unique_classes(board: Board2D, moves: List[Tuple[int, int]], card: int) -> List[Tuple[int, int]]:
    result = []
    _result_hashes = set()
    board = deepcopy(board)

    for row, col in moves:
        assert board[row][col] == 0, "board must be empty at `move` position"
        board[row][col] = card

        contains = False
        for symmetry in all_symmetries(board):
            if hash(str(symmetry)) in _result_hashes:
                contains = True
                break

        if not contains:
            _result_hashes.add(hash(str(board)))
            result.append((row, col))

        board[row][col] = 0

    return result
