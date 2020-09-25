from util.itertools import *


def test_BFSStack():
    res = []
    stack = BFSStack([1, 2, 3])
    for step, it in stack.next_step_iter():
        for v in it:
            res.append(v)
            if v < 10:
                stack.append(v * 10)
    assert stack.step == 2
    assert res == [1, 2, 3, 10, 20, 30]


def test_Direction():
    direction = Direction(4, 3, 4)
    assert set(direction.iter_next((0, 0))) == {(1, 0), (0, 1)}
    assert set(direction.iter_next((2, 3))) == {(2, 2), (1, 3)}
    assert set(direction.iter_next((1, 1))) == {(0, 1), (1, 2), (2, 1), (1, 0)}

    direction = Direction(8, 3, 4)
    assert len(list(direction.iter_next((1, 1)))) == 8
