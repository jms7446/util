from itertools import combinations

from ..data_structure import *


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

    xs[3] = 10
    tree.update(3, 10)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (sum(xs[i:j]), (i, j))


def test_SegmentTree_min():
    from itertools import combinations

    xs = [2, 3, 7, 4, 5, 9, 6, 1]
    tree = SegmentTree(xs, acc_func=min, init=float('inf'))
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (min(xs[i:j]), (i, j))

    xs[3] = 10
    tree.update(3, 10)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (min(xs[i:j]), (i, j))


def test_SegmentTree_max():
    from itertools import combinations

    xs = [2, 3, 7, 4, 5, 9, 6, 1]
    tree = SegmentTree(xs, acc_func=max, init=-float('inf'))
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (max(xs[i:j]), (i, j))

    xs[3] = 10
    tree.update(3, 10)
    for i, j in combinations(range(len(xs)), 2):
        assert (tree.get_range_value(i, j-1), (i, j)) == (max(xs[i:j]), (i, j))


def test_Tree_iter_preorder():
    values = range(7)
    edges = [(0, 1), (1, 2), (3, 2), (3, 4), (5, 1), (5, 6)]
    tree = Tree.from_values_and_edges(values, edges)
    traversed = [node.value for node in tree.iter_preorder()]
    assert traversed == [0, 1, 2, 3, 4, 5, 6]
