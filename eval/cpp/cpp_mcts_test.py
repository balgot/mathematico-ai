import _cpp_mcts as cpp


print(cpp.__doc__)
print(dir(cpp))

board = [[0] * 5] * 5
deck = [4 for _ in range(14)]
print(cpp.random_policy(board, deck))

card = 1
exp = .7090
max_sim = 10
max_time = 100
print(cpp.mcts(board, card, exp, max_sim, max_time, cpp.random_policy))

_printed = False
def policy(*args, **kwargs):
    global _printed
    if not _printed:
        _printed = True
        print(*args)
        print(**kwargs)
    return 1

print(cpp.mcts(board, card, exp, max_sim, max_time, policy))
