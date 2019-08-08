import pytest

from ..text import Match, AhocorasickWrapper, search_highlight, strip_margin, multi_replace, remove_4byte_unicode


def test_ahocorasick_wrapper_with_allow_substring_match():
    """ahocorasick 기본 동작 확인"""
    keywords = ['abcd', 'bc', 'bcd', 'abc', 'cde']
    text = 'xabcdey'
    kwtree = AhocorasickWrapper(keywords, allow_substring_match=True)
    assert kwtree.find_all(text) == [
        Match('abc', 1, 4),
        Match('bc', 2, 4),
        Match('abcd', 1, 5),
        Match('bcd', 2, 5),
        Match('cde', 3, 6),
    ]


def test_ahocorasick_wrapper_no_substring_match():
    """한 매칭이 다른 매칭에 완전히 포함되면(substring) 무시한다"""
    keywords = ['abcd', 'bc', 'bcd', 'abc', 'cde']
    text = 'xabcdey'
    kwtree = AhocorasickWrapper(keywords, allow_substring_match=False)
    assert kwtree.find_all(text) == [
        Match('abcd', 1, 5),
        Match('cde', 3, 6),
    ]


def test_ahocorasick_wrapper_with_empty_keywords():
    """빈 keywords가 들어와도 정상동작 해야 한다"""
    kwtree = AhocorasickWrapper([])
    assert kwtree.find_all('abc') == []


@pytest.mark.parametrize(['text', 'ptn_list', 'expected'], [
    ('ab cde fg', ['cde'], 'ab *cde* fg'),
    ('ab cde fg | ab cd fg', ['cd', 'cde'], 'ab *cde* fg | ab *cd* fg'),    # substring 관계 패턴, 긴 패턴 우선
    # ('')
])
def test_search_highlight(text, ptn_list, expected):
    assert search_highlight(text, ptn_list, mode='md') == expected


@pytest.mark.parametrize(['text', 'ptn_list', 'expected'], [
    ('ab cde fg', ['cde'], 'ab <b>cde</b> fg'),
    ('ab cde fg | ab cd fg', ['cd', 'cde'], 'ab <b>cde</b> fg | ab <b>cd</b> fg'),    # substring 관계 패턴, 긴 패턴 우선
])
def test_search_highlight_html(text, ptn_list, expected):
    assert search_highlight(text, ptn_list, mode='html') == expected


def test_strip_margin():
    s = '''
    ab c
    d e
     x
    '''
    assert strip_margin(s) == 'ab c\nd e\n x'


def test_multi_replace():
    string = "spam foo bar foo bar spam"
    substitutions = {"foo": "FOO", "bar": "BAR"}
    assert multi_replace(string, substitutions) == 'spam FOO BAR FOO BAR spam'


@pytest.mark.parametrize(['in_text', 'expected'], [
    ('가나다💕라마바사', '가나다라마바사'),
    ('abcdefghi', 'abcdefghi'),
])
def test_remove_4byte_unicode(in_text, expected):
    assert remove_4byte_unicode(in_text) == expected

