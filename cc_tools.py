import sys
import inspect

# sys.setrecursionlimit(1000000)


def eprint(*args, **kwargs):
    print(file=sys.stderr)
    print(*args, **kwargs, end='', file=sys.stderr)


def get_caller_filename():
    frame = inspect.stack()[2]      # We want caller's caller's name
    module = inspect.getmodule(frame[0])
    filename = module.__file__
    return filename
