import os
import logging
from configparser import ConfigParser


class SingletonType(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class CustomLogger(metaclass=SingletonType):
    _logger = None

    def __init__(self):
        self._logger = logging.getLogger("crumbs")
        self._logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')

        import datetime
        now = datetime.datetime.now()

        dirname = './logs'
        if not os.path.isdir(dirname):
            os.mkdir(dirname)
        file_handler = logging.FileHandler(dirname + "/All_" + now.strftime("%Y-%m-%d_%H%M%S") + ".log")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        self._logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.WARNING)
        self._logger.addHandler(stream_handler)

    def get_logger(self):
        return self._logger


class MyConfigParser(ConfigParser):
    """ConfigParser 에 to_dict 를 추가한 클래스

    from_fn 은 강제로 unicode 로 변환한다.
    from_fp 는 입력된 stream 의 string type 을 유지한다.
    """

    @classmethod
    def from_fp(cls, fp):
        parser = cls()
        parser.read_file(fp)
        return parser

    @classmethod
    def from_fn(cls, fn):
        with open(fn, encoding="utf8") as fp:
            return cls.from_fp(fp)

    def to_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d
