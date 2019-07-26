import pytest

from ..text import Matcher, StateMatcher, Match, AhocorasickWrapper


################################################################################
# AhocorasickWapper
################################################################################

def test_ahocorasick_wrapper_with_allow_substring_match():
    """ahocorasick 기본 동작 확인"""
    keywords = ['abcd', 'bc', 'bcd', 'abc', 'cde']
    haystack = 'xabcdey'
    kwtree = AhocorasickWrapper(keywords, allow_substring_match=True)
    assert list(kwtree.find_all(haystack)) == [
        ('abc', 1, 4),
        ('bc', 2, 4),
        ('abcd', 1, 5),
        ('bcd', 2, 5),
        ('cde', 3, 6),
    ]


def test_ahocorasick_wrapper_no_substring_match():
    """한 매칭이 다른 매칭에 완전히 포함되면(substring) 무시한다"""
    keywords = ['abcd', 'bc', 'bcd', 'abc', 'cde']
    haystack = 'xabcdey'
    kwtree = AhocorasickWrapper(keywords, allow_substring_match=False)
    assert list(kwtree.find_all(haystack)) == [
        ('abcd', 1, 5),
        ('cde', 3, 6),
    ]


def test_matcher_basic_match():
    keywords = ['abc', '사랑']
    # 앞 뒤로 공백 제외 2글자로 snippet (영문, 한글 동일)
    matcher = Matcher(keywords=keywords, snippet_window_size=2)

    assert list(matcher.match('xyz 안녕하세요')) == []
    assert list(matcher.match('가 나 다 abc de f')) == [
        Match('abc', '나 다 abc de'),
    ]
    assert list(matcher.match('가 나 다 abc 라 마 사랑 하늘 end')) == [
        Match('abc', '나 다 abc 라 마'),
        Match('사랑', '라 마 사랑 하늘'),
    ]


@pytest.mark.parametrize(['pre_input', 'cur_input', 'expected'], [
    ('', 'xyz 안녕하세요', []),
    ('', '가 나 다 abc de f', [('', '나 다 abc de')]),
    ('가 나 다 abc de f', '가 나 다 abc de f', []),   # 동일한 입력
    ('가 나 다 abc de f', '가 나 다abcde f', []),   # 공백만 다름
    ('가 나 다 abc de f', '가 나 도 abc de f', [('다 abc de', '도 abc de')]),   # 키워드 주변이 변함
])
def test_state_matcher_basic_match1(pre_input, cur_input, expected):
    """StateMatcher는 이전 문자열을 참조해서 keyword 주변에 변화가 있지 않으면 무시하는지 확인"""
    keywords = ['abc', '사랑']
    # 앞 뒤로 공백 제외 2글자로 snippet (영문, 한글 동일)
    matcher = StateMatcher(keywords=keywords, snippet_window_size=1, check_window_size=1)

    matcher.match(pre_input)
    assert list(matcher.match(cur_input)) == expected
