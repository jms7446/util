import textwrap
from io import StringIO

from ..custom import MyConfigParser


def test_my_config_parser():
    config_file = StringIO(textwrap.dedent("""\
        [util_test]
        key1 = 1
        key2 = a"""))
    config = MyConfigParser.from_fp(config_file).to_dict()
    assert config['util_test']['key1'] == '1'
    assert config['util_test']['key2'] == 'a'
