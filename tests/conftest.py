import os
from unittest.mock import patch
from datetime import datetime, timedelta
import tempfile
import shutil

import pytest

INIT_TIME = datetime(2019, 5, 1, 16, 30, 0, 16162)


@pytest.fixture
def watch():
    """util.time.watch를 mocking한다

    watch.now는 watch.sleep이 호출될 때만 변경된다.
    """
    with patch('util.time.watch') as watch:
        watch.now.return_value = INIT_TIME

        def sleep_effect(s):
            watch.now.return_value += timedelta(seconds=s)
        watch.sleep.side_effect = sleep_effect

        yield watch


@pytest.fixture
def temp_dir():
    dir_path = tempfile.mkdtemp()
    os.chdir(dir_path)
    yield dir_path
    shutil.rmtree(dir_path)
