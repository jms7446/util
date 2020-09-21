from util.mymath import *


def test_number_to_digits():
    assert number_to_digits(12) == [1, 2]
    assert number_to_digits(12, base=3) == [1, 1, 0]
    assert number_to_digits(12, base=3, length=5) == [0, 0, 1, 1, 0]


def test_digits_to_number():
    assert digits_to_number([1, 2]) == 12
    assert digits_to_number([1, 1, 0], base=3) == 12


def test_iter_primes():
    assert list(iter_primes(10)) == [2, 3, 5, 7]
    assert list(iter_primes(11, begin=5)) == [5, 7, 11]


def test_combination():
    assert nCr(6, 2) == 15
    assert nCr(6, 4) == 15
    assert nCr(1, 1) == 1
    assert nCr(1, 0) == 1


def test_permutation_with_dup():
    assert permutations_with_dup((4, )) == 1
    assert permutations_with_dup((1, 1, 1, 1)) == 24
    assert permutations_with_dup((3, 1)) == 4
