from itertools import combinations
import random

from ..data_structure import *
from util import *


def test_FenwickTree():
    xs = [2, 3, 7, 4, 5, 9, 6, 1]
    tree = FenwickTree(xs)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (sum(xs[i:j]), (i, j))

    diff = 3
    xs[3] += diff
    tree.update(3, 3)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (sum(xs[i:j]), (i, j))


def test_KMP():
    assert KMP('ababaca').table == [0, 0, 1, 2, 3, 0, 1]
    assert list(KMP('abababc').search('ababababc abababd')) == [2]
    assert list(KMP('abcdabd').search('abc abcdab abcdabcdabde')) == [15]


def test_SegmentTree_add():
    xs = [2, 3, 7, 4, 5, 9, 6, 1]
    tree = SegmentTree(xs)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (sum(xs[i:j]), (i, j))

    xs[3] += 6
    tree.update(3, 6)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (sum(xs[i:j]), (i, j))


def test_SegmentTree_min():
    from itertools import combinations

    xs = [2, 3, 7, 4, 5, 9, 6, 1]
    tree = SegmentTree(xs, acc_func=min, init=float('inf'))
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (min(xs[i:j]), (i, j))

    xs[3] += 6
    tree.update(3, 6)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (min(xs[i:j]), (i, j))


def test_SegmentTree_max():
    from itertools import combinations

    xs = [2, 3, 7, 4, 5, 9, 6, 1]
    tree = SegmentTree(xs, acc_func=max, init=-float('inf'))
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (max(xs[i:j]), (i, j))

    xs[3] += 6
    tree.update(3, 6)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (max(xs[i:j]), (i, j))


def gen_range(n):
    left, right = random.randint(0, n - 1), random.randint(0, n - 1)
    if left > right:
        left, right = right, left
    return left, right


def test_SegmentTreeLazy_update():
    for _ in range(100):
        xs = list(range(10))
        tree = SegmentTreeLazy(xs)
        history = []
        for _ in range(10):
            left, right = gen_range(len(xs))
            diff = random.randint(-3, 3)
            for i in range(left, right + 1):
                xs[i] += diff
            tree.range_update(left, right, diff)
            history.append((left, right, diff))

        left, right = gen_range(len(xs))
        if tree.get_range_value(left, right) != sum(xs[left:right+1]):
            eprint('history', history)
            eprint('xs, left, right', xs, left, right)
            assert tree.get_range_value(left, right) == sum(xs[left:right+1])


def test_SegmentTreeLazy():
    xs = [0, 1, 2, 3, 4]
    tree = SegmentTreeLazy(xs)
    tree.range_update(4, 4, 0)
    assert tree.get_range_value(2, 4) == 9


def test_SegmentTreeLazy_base():
    xs = [2, 3, 7, 4, 5, 9, 6, 1]
    tree = SegmentTreeLazy(xs)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (sum(xs[i:j]), (i, j))


def test_Tree_iter_preorder():
    values = range(7)
    edges = [(0, 1), (1, 2), (3, 2), (3, 4), (5, 1), (5, 6)]
    tree = Tree.from_values_and_edges(values, edges)
    traversed = [node.value for node in tree.iter_preorder()]
    assert traversed == [0, 1, 2, 3, 4, 5, 6]
