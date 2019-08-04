from datetime import timedelta, datetime, time
from unittest.mock import Mock

import pytest

from ..time import IntervalLocker, TimeRangeLocker, wait_when_error


def test_locker_wait(watch):
    """IntervalLocker 가 interval 동안 wait 한 후의 시간이 interval 이 지난 후인지 확인한다."""
    lock_seconds = 5
    check_sec = 0.1
    locker = IntervalLocker(lock_seconds, check_sec=check_sec)

    # 최초 wait() 는 대기하지 않는다.
    t0_start = watch.now()
    locker.wait()
    assert watch.now() == t0_start

    # interval만큼 대기했는지 확인
    t1_start = watch.now()
    locker.wait()
    t1_end = watch.now()
    expected = t1_start + timedelta(seconds=lock_seconds)
    # assert expected <= t1_end < expected + timedelta(seconds=check_sec)
    assert expected <= t1_end

    # 다른 작업으로 시간이 지나면 waiting하는 시간이 짧아져서 interval이 유지된다.
    watch.sleep(3)   # 다른 작업
    locker.wait()
    t2_end = watch.now()
    # 기준 시간은 이전 wait가 끝난 시간이 된다.
    expected = t1_end + timedelta(seconds=lock_seconds)
    assert expected <= t2_end < expected + timedelta(seconds=check_sec)

    # 다른 작업으로 interval 보다 오랜 시간이 지났으므로 안에서 시간을 소비하지 않는다.
    watch.sleep(8)
    t3_start = watch.now()
    locker.wait()
    t3_end = watch.now()
    assert t3_start == t3_end


def test_interval_locker_reset_if_free(watch):
    """리셋 시간이 되었는지를 외부에서 loop을 돌면서 체크할 때 사용하는 함수이다. 제대로 동작하는지 확인한다."""
    lock_seconds = 5
    locker = IntervalLocker(lock_seconds)

    # 처음에는 free 이므로 True 반환
    assert locker.is_free_then_lock()

    # 이제 5초가 흘러야 True를 반환한다.

    # reset_if_free를 호출해도 내부적으로 sleep이 없으므로 시간이 흐르지 않는다
    now = watch.now()
    assert not locker.is_free_then_lock()
    assert watch.now() == now

    # 4초가 흘러도 잠겨있음
    watch.sleep(4)
    assert not locker.is_free_then_lock()

    # 이제 5초가 흐르면 열린다
    watch.sleep(1)
    assert locker.is_free_then_lock()

    # 다시 잠김
    watch.sleep(1)
    assert not locker.is_free_then_lock()


def test_interval_lock_init_lock_false(watch):
    """init_lock=False(기본값) 하면 시작했을 때 열려있다"""
    locker = IntervalLocker(5)
    assert locker.is_free_then_lock()

    watch.sleep(1)
    assert not locker.is_free_then_lock()


def test_interval_lock_init_lock_true(watch):
    """init_lock=True로 하면 시작했을 때 잠겨있다"""
    locker = IntervalLocker(5, init_lock=True)
    assert not locker.is_free_then_lock()

    watch.sleep(3)
    assert not locker.is_free_then_lock()

    watch.sleep(2)
    assert locker.is_free_then_lock()


@pytest.mark.parametrize(['range_str', 'in_hours', 'not_in_hours'], [
    ('3 ~ 6', [3, 4, 5], [1, 2, 6, 7]),
    ('3~6', [3, 4, 5], [1, 2, 6, 7]),
    ('23 ~ 3', [23, 0, 2], [22, 3, 4]),
    ('', [], range(24)),
    (None, [], range(24)),
])
def test_time_range_contains(range_str, in_hours, not_in_hours):
    """in 이 정상적으로 동작하는지 확인"""
    time_range = TimeRangeLocker(range_str)
    for in_hour in in_hours:
        assert time(in_hour, 2, 3) in time_range
    for not_in_hour in not_in_hours:
        assert time(not_in_hour, 2, 3) not in time_range


def test_time_range_wait_until_waiting(watch):
    """time_range 속에 포함되어 대기한다."""
    watch.now.return_value = datetime(2019, 5, 1, 16, 30, 0, 16162)

    time_range = TimeRangeLocker('12~18')
    time_range.wait()
    t2 = watch.now()
    assert t2 == datetime(2019, 5, 1, 18, 0, 0, 16162)


def test_time_range_wait_until_no_waiting(watch):
    """time_range 에 포함되지 않으므로 대기하지 않는다."""
    watch.now.return_value = datetime(2019, 5, 1, 16, 30, 0, 16162)

    time_range = TimeRangeLocker('2~5')
    t1 = watch.now()
    time_range.wait()
    t2 = watch.now()
    assert t1 == t2


################################################################################
# wait_when_error
################################################################################

def test_wait_when_error_return_right_value(watch):
    """default_result 값을 정상적으로 처리하고 있는가"""
    func = Mock()
    wrapped = wait_when_error(default_result=0)(func)

    func.side_effect = [1]
    assert wrapped() == 1

    func.side_effect = [Exception]
    assert wrapped() == 0


@pytest.mark.parametrize(['init_wait_time', 'results', 'is_reset', 'expected_wait_times'], [
    (6, [1, 1], False, [0, 0]),
    (4, [Exception, Exception], False, [4, 8]),
    (6, [Exception, Exception], False, [6, 10]),
    (6, [1, Exception], False, [0, 3]),
    (3, [1, Exception], False, [0, 2]),
    (8, [1, Exception], True, [0, 2]),
])
def test_wait_when_error_wait_time_correctly(init_wait_time, results, expected_wait_times, is_reset, watch):
    """error가 생겼을 때 대기하는 시간의 증감이 제대로 이루어지는지 확인"""
    wrapper = wait_when_error(default_result=0, up_ratio=2, down_ratio=0.5, min_wait_time=2, max_wait_time=10,
                              reset_when_no_err=is_reset)
    wrapper.wait_time = init_wait_time
    wrapped = wrapper(Mock(side_effect=results))

    t = watch.now()
    wrapped()
    assert (watch.now() - t).seconds == expected_wait_times[0]

    t = watch.now()
    wrapped()
    assert (watch.now() - t).seconds == expected_wait_times[1]


def test_wait_when_error_as_decorator(watch):
    """decorator로 동작하는지 간단한 정도로만 확인"""
    @wait_when_error(default_result=0, min_wait_time=2)
    def func(a, b):
        if a == 0:
            raise Exception
        return a + b

    t = watch.now()
    assert func(1, 2) == 3
    assert (watch.now() - t).seconds == 0

    t = watch.now()
    assert func(0, 2) == 0
    assert (watch.now() - t).seconds == 2
