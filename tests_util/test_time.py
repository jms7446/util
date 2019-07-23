from datetime import timedelta, datetime, time

import pytest

from util.time import IntervalLocker, TimeRangeLocker


def test_locker_wait(watch):
    """IntervalLocker 가 interval 동안 wait 한 후의 시간이 interval 이 지난 후인지 확인한다."""
    lock_seconds = 5
    check_sec = 0.1
    locker = IntervalLocker(lock_seconds, watch.now(), check_sec=check_sec)

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
