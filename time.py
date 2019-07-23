import time
import datetime
from abc import ABC, abstractmethod


class _Watch:
    """now and sleep 관리, 모듈 변수로 watch를 생성하고, 시간 관리용으로 사용한다"""

    @staticmethod
    def now():
        return datetime.datetime.now()

    @staticmethod
    def sleep(sec):
        time.sleep(sec)

    def now_dttm(self):
        return self.now().strftime('%Y%m%d-%H%M%S')

    def now_dt(self):
        return self.now().strftime('%Y%m%d')


watch = _Watch()


class Locker(ABC):

    def __init__(self, check_sec):
        self.check_sec = check_sec

    @abstractmethod
    def wait(self):
        """"lock이 풀릴 때까지 대기한다"""


class IntervalLocker(Locker):
    """wait()가 호출되면 이전 wait()가 return된 시간으로 부터 interval초 이후가 될 때까지 대기한다"""

    def __init__(self, interval, free_time=None, check_sec=1):
        super().__init__(check_sec)
        self.interval = interval
        self.free_time = free_time or watch.now()

    def wait(self):
        while True:
            cur_time = watch.now()
            if cur_time >= self.free_time:
                break
            watch.sleep(self.check_sec)
        self.free_time = cur_time + datetime.timedelta(seconds=self.interval)


class TimeRangeLocker(Locker):
    """wait()가 호출되면 start ~ end 사이의 시간이라면 대기한다"""

    def __init__(self, range_ptn='', check_sec=60):
        super().__init__(check_sec)
        if range_ptn:
            start, end = [int(x) for x in range_ptn.split('~')]
            self.start_time = datetime.time(start, 0, 0)
            self.end_time = datetime.time(end, 0, 0)
        else:
            self.start_time = None
            self.end_time = None

    def wait(self):
        while watch.now().time() in self:
            watch.sleep(self.check_sec)

    def __contains__(self, tm):
        if self.start_time is None:
            return False
        elif self.start_time <= self.end_time:
            return self.start_time <= tm < self.end_time
        else:
            return self.start_time <= tm or tm < self.end_time