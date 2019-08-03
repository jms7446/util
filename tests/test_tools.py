import os
import pytest

from .. import tools


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


def test_text_dum_load(tmpdir):
    text = 'hi, 안녕하세요. \n ! \t'
    file_path = os.path.join(tmpdir, 'tmp.pkl')

    tools.text_write(text, file_path)
    assert tools.text_read(file_path) == text
