from typing import List
from dataclasses import dataclass
from inspect import cleandoc
import re

from ahocorasick import Automaton


@dataclass
class Match:
    keyword: str
    start: int
    end: int


class AhocorasickWrapper:
    def __init__(self, keywords: List[str], allow_substring_match=False):
        self.kwtree = self._make_kwtree(keywords)
        self.allow_substring_match = allow_substring_match

    def find_all(self, text: str) -> List[Match]:
        if self.kwtree:
            ahocorasick_result = self.kwtree.iter(text)
            matches = self._alt_result_to_match(ahocorasick_result)
            if self.allow_substring_match:
                return matches
            else:
                return self._exclude_substring_match(matches)
        else:
            return []

    @staticmethod
    def _make_kwtree(keywords):
        if keywords:
            kwtree = Automaton()
            for keyword in keywords:
                kwtree.add_word(keyword, keyword)
            kwtree.make_automaton()
        else:
            kwtree = None
        return kwtree

    @staticmethod
    def _alt_result_to_match(ahocorasick_results) -> List[Match]:
        """pyahocorasick 에서 나오는 end 값은 매칭된 마지막 index, python slicing 개념의 start, end로 바꾼다
        [(kw, end_index), ...] -> [(kw, start, end), ...]
        """
        return [Match(kw, end_index + 1 - len(kw), end_index + 1) for end_index, kw in ahocorasick_results]

    @staticmethod
    def _exclude_substring_match(matches: List[Match]):
        """다름 매칭에 substring으로 포함되는 매칭은 무시한다"""
        matches = sorted(matches, key=lambda m: (m.start, -m.end))
        non_substring_matches = []
        max_end = 0
        for match in matches:
            if match.end > max_end:
                non_substring_matches.append(match)
                max_end = match.end
        return non_substring_matches


def search_highlight(text, ptn_list, mode='md') -> str:
    if mode in ['md', 'markdown']:
        target_format = '*{}*'
    elif mode in ['html', 'htm']:
        target_format = '<b>{}</b>'
    else:
        raise ValueError(f'Unknown mode: {mode}')

    # 긴 패턴의 replace를 우선한다.
    ptn_list = sorted(ptn_list, key=lambda x: len(x), reverse=True)

    # substring 관계에 있는 패턴을 보호하기 위해서 패턴을 찾는 동안에는 mid_ptn으로 변환했다가, 패턴을 다 찾은 후 일괄 변환한다
    mid_ptn_map = {}
    for i, ptn in enumerate(ptn_list):
        mid_ptn = f'__|{i}|__'
        target = target_format.format(ptn)
        text = text.replace(ptn, mid_ptn)
        mid_ptn_map[mid_ptn] = target

    # 일괄 변경
    for mid_ptn, target in mid_ptn_map.items():
        text = text.replace(mid_ptn, target)

    return text


def strip_margin(text):
    """Use inspect.cleandoc instead"""
    return cleandoc(text)


def multi_replace(string, substitutions):
    """dict으로 들어온 매핑을 사용해 string을 replace한다
    ref : https://gist.github.com/carlsmith/b2e6ba538ca6f58689b4c18f46fef11c?fbclid=IwAR3Aw1StDSDbQIHY9aZHca0A37e-b9v1RCsE9jofRmBKFrT9w-ZsWRWjsBI
    """
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


try:
    high_points = re.compile('[\U00010000-\U0010ffff]')
except re.error:
    # UCS-2 build
    high_points = re.compile('[\uD800-\uDBFF][\uDC00-\uDFFF]')


def remove_4byte_unicode(text):
    """4byte unicode 제거 """
    return high_points.sub('', text)

