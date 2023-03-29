primes = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,87,89,91,97]
alist = [[1, 2, 3, 4, 5]] * 5
MOD = 143 * 147 * 153

from itertools import chain


def pows():
    x = 0
    for p, el in zip(primes, chain(*alist)):
        x = (x + p**el) % MOD
    # p = -1
    # for row in alist:
    #     for el in row:
    #         x += (primes[(p := p + 1)]**el)
    return x % MOD


def sstr():  # faster, but is randomized
    return hash(str(alist))
