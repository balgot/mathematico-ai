import _cpp_mcts as cpp


print(cpp.__doc__)
print(dir(cpp))

board = [[0] * 5] * 5
deck = [4 for _ in range(14)]
card = 1
max_time = 100
print(cpp.mcts(board, card, max_time))
