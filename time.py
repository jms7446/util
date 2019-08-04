import time
import datetime
from abc import ABC, abstractmethod
import contextlib
import logging


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

    def __init__(self, interval, init_lock=False, check_sec=1):
        super().__init__(check_sec)
        self.interval = interval
        self.free_time = watch.now()
        if init_lock:
            self.free_time += datetime.timedelta(seconds=interval)

    def wait(self):
        while True:
            cur_time = watch.now()
            if cur_time >= self.free_time:
                break
            watch.sleep(self.check_sec)
        self.free_time = cur_time + datetime.timedelta(seconds=self.interval)

    def is_free_then_lock(self):
        """free time이 되었으면 free time을 재설정하고 True를 리턴, 아니면 그냥 False를 리턴"""
        cur_time = watch.now()
        if cur_time >= self.free_time:
            self.free_time = cur_time + datetime.timedelta(seconds=self.interval)
            return True
        else:
            return False


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


class wait_when_error:
    """Exception이 발생하면 대기한다. Exception이 발생할 때마다 대기시간이 지수적으로 늘어나고 발생하지 않으면 지수적으로 감소한다"""

    def __init__(self, default_result, min_wait_time=60.0, max_wait_time=3600.0,
                 up_ratio=2.0, down_ratio=0.5, reset_when_no_err=False, logging_exception=True):
        self.default_result = default_result
        self.min_wait_time = min_wait_time
        self.max_wait_time = max_wait_time
        self.up_ratio = up_ratio
        self.down_ratio = down_ratio
        self.reset_when_no_error = reset_when_no_err
        self.logging_exception = logging_exception
        self.wait_time = min_wait_time
        if up_ratio <= 1.0:
            raise ValueError(f'up_ratio must bigger than 1.0: {up_ratio}')
        if down_ratio >= 1.0:
            raise ValueError(f'down_ratio must smaller than 1.0: {down_ratio}')

    def __call__(self, func):
        @contextlib.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception:
                if self.logging_exception:
                    logging.exception(f'Exception occurred and wait {self.wait_time}sec')
                watch.sleep(self.wait_time)
                self.wait_time = min(self.max_wait_time, self.wait_time * self.up_ratio)
                result = self.default_result
            else:
                if self.reset_when_no_error:
                    self.wait_time = self.min_wait_time
                else:
                    self.wait_time = max(self.min_wait_time, self.wait_time * self.down_ratio)
            return result
        return wrapper
