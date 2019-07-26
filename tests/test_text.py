import pytest

from ..text import Monitor, DiffMonitor, Match, AhocorasickWrapper, MonitorResult


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


################################################################################
# Monitor
################################################################################

def test_matcher_basic_match():
    keywords = ['abc', '사랑']
    # 앞 뒤 3글자로(공백포함) snippet 생성. 영문, 한글 동일한 사이즈로 취급됨
    monitor = Monitor(keywords=keywords, snippet_window_size=3)

    assert monitor.check('xyz 안녕하세요').results == []
    assert monitor.check('가 나 다 abc de f').results == [
        MonitorResult('abc', ' 다 abc de'),
    ]
    assert monitor.check('가 나 다 abc 라마 사랑 하늘 end').results == [
        MonitorResult('abc', ' 다 abc 라마'),
        MonitorResult('사랑', '라마 사랑 하늘'),
    ]


@pytest.mark.parametrize(['pre_input', 'cur_input', 'removed', 'added'], [
    ('', 'xyz 안녕하세요', [], []),
    ('', '가나다 abc de f', [], [MonitorResult('abc', '나다 abc de')]),   # 생김
    ('가나다 abc de f', '', [MonitorResult('abc', '나다 abc de')], []),   # 없어짐
    ('가나다 abc de f', '가나다 abc de f', [], []),   # 동일한 입력
    # ('가나다 abc de f', '가나다abcde f', [], []),   # 공백만 다름 (구현안됨)
    ('가나다 abc de f', '가나도 abc de f', [MonitorResult('abc', '나다 abc de')], [MonitorResult('abc', '나도 abc de')]),
])
def test_state_matcher_basic_match1(pre_input, cur_input, removed, added):
    """StateMatcher는 이전 문자열을 참조해서 keyword 주변에 변화가 있지 않으면 무시하는지 확인"""
    keywords = ['abc', '사랑']
    # 앞 뒤로 공백 제외 2글자로 snippet (영문, 한글 동일)
    monitor = DiffMonitor(keywords=keywords, snippet_window_size=3)

    monitor.check(pre_input)
    report = monitor.check(cur_input)
    assert report.removed_results == removed
    assert report.added_results == added
