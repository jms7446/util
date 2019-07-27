import pytest

from ..text import Match, AhocorasickWrapper, search_highlight


################################################################################
# Match
################################################################################

def test_match_make_snippet():
    match = Match('abc', 3, 6, 'xy abc fgh')
    assert match.make_snippet(window_size=1) == ' abc '
    assert match.make_snippet(window_size=2) == 'y abc f'
    assert match.make_snippet(window_size=3) == 'xy abc fg'
    assert match.make_snippet(window_size=9) == 'xy abc fgh'


################################################################################
# AhocorasickWapper
################################################################################

def test_ahocorasick_wrapper_with_allow_substring_match():
    """ahocorasick 기본 동작 확인"""
    keywords = ['abcd', 'bc', 'bcd', 'abc', 'cde']
    text = 'xabcdey'
    kwtree = AhocorasickWrapper(keywords, allow_substring_match=True)
    assert kwtree.find_all(text) == [
        Match('abc', 1, 4, text),
        Match('bc', 2, 4, text),
        Match('abcd', 1, 5, text),
        Match('bcd', 2, 5, text),
        Match('cde', 3, 6, text),
    ]


def test_ahocorasick_wrapper_no_substring_match():
    """한 매칭이 다른 매칭에 완전히 포함되면(substring) 무시한다"""
    keywords = ['abcd', 'bc', 'bcd', 'abc', 'cde']
    text = 'xabcdey'
    kwtree = AhocorasickWrapper(keywords, allow_substring_match=False)
    assert list(kwtree.find_all(text)) == [
        Match('abcd', 1, 5, text),
        Match('cde', 3, 6, text),
    ]


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