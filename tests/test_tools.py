import os
from os.path import join as pjoin
from pathlib import Path
import pytest

from .. import tools


def test_remote_ssh_command():
    host = 'host'
    cmd = 'mv'
    args = ['my name.txt', 'your name.txt']

    assert tools.make_remote_ssh_command(host, cmd, *args).strip() == """
        ssh host 'mv "my name.txt" "your name.txt"'
    """.strip()


@pytest.mark.parametrize(['file_path', 'suffix', 'expected'], [
    ('/dir/aa.txt', 'suffix', '/dir/aa_suffix.txt'),
    ('dir/aa.txt', 'suffix', 'dir/aa_suffix.txt'),
    ('aa.txt', 'suffix', 'aa_suffix.txt'),
    ('/dir/aa', 'suffix', '/dir/aa_suffix'),
    ('/dir/', 'suffix', '/dir/_suffix'),  # 애매하다
    ('.', 'suffix', '_suffix.'),        # 애매하다
    ('/dir/.txt', 'suffix', '/dir/_suffix.txt'),  # 흔한 케이스는 아니다
    ('/dir/aa.', 'suffix', '/dir/aa_suffix.'),  # 흔한 케이스는 아니다
])
def test_add_file_name_suffix(file_path, suffix, expected):
    assert tools.add_file_name_suffix(file_path, suffix) == expected


@pytest.mark.parametrize(['url', 'keeps', 'expected'], [
    ('http://a.b.com/path/file.html?z=1&y=2&x=3', ['x', 'z'], 'http://a.b.com/path/file.html?x=3&z=1'),
    ('/zboard/view.php?id=freeboard&page=1&divpage=1&no=65', ['no', 'id'], '/zboard/view.php?no=65&id=freeboard'),
])
def test_norm_url_params_with_keep(url, keeps, expected):
    assert tools.norm_url_query_string_with_keep(url, keeps) == expected


@pytest.mark.parametrize(['text', 'expected'], [
    ('a  b', 'a b'),
    (' a  b ', 'a b'),
    ('a\nb\t', 'a b'),
    ('하늘  사 \t랑', '하늘 사 랑'),
])
def test_norm_whitespace(text, expected):
    assert tools.norm_whitespace(text) == expected


@pytest.mark.parametrize(['texts_list', 'expected'], [
    ([['a', 'b'], ['c', 'd']], 'a\tb\nc\td'),
    ([['a x ', '\t b \n'], ['c', ' d ']], 'a x\tb\nc\td'),
])
def test_flat_text_with_sep(texts_list, expected):
    assert tools.flat_text_with_sep(texts_list) == expected


@pytest.mark.parametrize(['url', 'expected'], [
    ('http://a.b.com/x/do?p=1&q=2', '/x/do?p=1&q=2'),
    ('//a.b.com/x/do?p=1&q=2', '/x/do?p=1&q=2'),
    ('/x/do?p=1&q=2', '/x/do?p=1&q=2'),
    ('do?p=1&q=2', '/r/do?p=1&q=2'),
])
def test_make_abs_url(url, expected):
    base_url = 'http://d.e.com/r/h'
    assert tools.make_abs_url(base_url, url) == expected


def test_pickle_dump_load(tmpdir):
    obj = {'a': 1, 'b': 2}
    file_path = os.path.join(tmpdir, 'tmp.pkl')
    tools.pickle_dump(obj, file_path)
    loaded_obj = tools.pickle_load(file_path)

    assert loaded_obj == obj


@pytest.fixture
def move_file_temp_dir(temp_dir):
    os.chdir(temp_dir)
    os.makedirs('a')
    os.makedirs('b/b_sub')
    Path('a/x.txt').touch()
    Path('b/x.txt').touch()
    yield temp_dir


@pytest.mark.parametrize(['src_path', 'dst_path', 'overwrite'], [
    ('a/x.txt', 'b/y.txt', False),
    ('a/x.txt', 'b/a.txt', True),
    ('a/x.txt', 'c/d/y.txt', False),
])
def test_move_file_success(src_path, dst_path, overwrite, move_file_temp_dir):
    tools.move_file(src_path, dst_path, overwrite=overwrite)
    assert os.path.isfile(dst_path)


@pytest.mark.parametrize(['src_path', 'dst_path', 'overwrite', 'exception'], [
    ('a/x.txt', 'b/x.txt', False, ValueError),
    ('a/x.txt', 'b/b_sub', True, ValueError),
])
def test_move_file_fail(src_path, dst_path, overwrite, exception, move_file_temp_dir):
    with pytest.raises(exception):
        tools.move_file(src_path, dst_path, overwrite=overwrite)
    assert os.path.isfile(src_path)


@pytest.mark.parametrize(['src_path', 'dst_dir', 'overwrite'], [
    ('a/x.txt', 'b/b_sub', False),
    ('a/x.txt', 'b', True),
    ('a/x.txt', 'c/d', False),
])
def test_move_file_to_dir_success(src_path, dst_dir, overwrite, move_file_temp_dir):
    tools.move_file_to_dir(src_path, dst_dir, overwrite=overwrite)
    dst_path = pjoin(dst_dir, src_path.split('/')[-1])
    assert os.path.isfile(dst_path)


@pytest.mark.parametrize(['src_path', 'dst_dir', 'overwrite', 'exception'], [
    ('a/x.txt', 'b', False, ValueError),
    ('a/x.txt', 'b/x.txt', True, ValueError),
])
def test_move_file_to_dir_fail(src_path, dst_dir, overwrite, exception, move_file_temp_dir):
    with pytest.raises(exception):
        tools.move_file_to_dir(src_path, dst_dir, overwrite=overwrite)
    assert os.path.isfile(src_path)


def test_text_dump_load(tmpdir):
    text = 'hi, 안녕하세요. \n ! \t'
    file_path = os.path.join(tmpdir, 'tmp.pkl')

    tools.text_write(text, file_path)
    assert tools.text_read(file_path) == text


@pytest.mark.parametrize(['dic1', 'dic2', 'expected'], [
    ({'a': 1, 'b': 2}, {'a': 3, 'b': 4}, True),
    ({'a': 1, 'b': 2}, {2: 2}, False),
    ({'a': 1, 'b': 2}, {'a': 3, 'b': 'text'}, False),
    ({'a': 1, 'b': 2}, {'a': 3, 'other_key': 4}, False),
    ({'a': 1, 'nested': {'n1': 'x', 'n2': 1}}, {'a': 3, 'nested': {'n1': 'y', 'n2': 2}}, True),
    ({'a': 1, 'nested': {'n1': 'x', 'n2': 1}}, {'a': 3, 'nested': {'n1': 'y', 'n2': False}}, False),
])
def test_is_equal_structured_dict(dic1, dic2, expected):
    assert tools.is_equal_structured_dict(dic1, dic2) == expected
