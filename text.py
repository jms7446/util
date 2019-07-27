from typing import List
from dataclasses import dataclass

from ahocorasick import Automaton


@dataclass
class Match:
    keyword: str
    start: int
    end: int
    text: str

    def make_snippet(self, window_size=2):
        snippet_start = max(0, self.start - window_size)
        snippet_end = min(len(self.text), self.end + window_size)
        return self.text[snippet_start:snippet_end]


class AhocorasickWrapper:
    def __init__(self, keywords: List[str], allow_substring_match=False):
        self.kwtree = Automaton()
        self.allow_substring_match = allow_substring_match
        for keyword in keywords:
            self.kwtree.add_word(keyword, keyword)
        self.kwtree.make_automaton()

    def find_all(self, text: str) -> List[Match]:
        ahocorasick_result = self.kwtree.iter(text)
        start_end_result = self._alt_result_format(ahocorasick_result)
        matches = [Match(kw, start, end, text) for kw, start, end in start_end_result]
        if self.allow_substring_match:
            return matches
        else:
            return self._exclude_substring_match(matches)

    @staticmethod
    def _alt_result_format(ahocorasick_results):
        """pyahocorasick 에서 나오는 end 값은 매칭된 마지막 index, python slicing 개념의 start, end로 바꾼다
        [(kw, end_index), ...] -> [(kw, start, end), ...]
        """
        return [(kw, end_index + 1 - len(kw), end_index + 1) for end_index, kw in ahocorasick_results]

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


def search_highlight(text, ptn_list, mode='md'):
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
