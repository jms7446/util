import textwrap
from io import StringIO

from ..custom import MyConfigParser, SingletonInstance


def test_my_config_parser():
    config_file = StringIO(textwrap.dedent("""\
        [util_test]
        key1 = 1
        key2 = a"""))
    config = MyConfigParser.from_fp(config_file).to_dict()
    assert config['util_test']['key1'] == '1'
    assert config['util_test']['key2'] == 'a'


def test_SingletonInstance():
    class MySingleton(SingletonInstance):
        def __init__(self):
            self.x = 0
            self.y = 1

    m1 = MySingleton.instance()
    m1.x = 10
    m1.y = 11

    m2 = MySingleton.instance()
    assert m2.x == 10
    assert m2.y == 11

    m2.x = 20
    assert m1.x == 20
