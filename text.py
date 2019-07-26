from typing import List
from dataclasses import dataclass, field

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


@dataclass
class MonitorResult:
    keyword: str
    snippet: str


@dataclass
class MonitorReport:
    results: List[MonitorResult] = field(default_factory=list)


@dataclass
class DiffMonitorReport:
    removed_results: List[MonitorResult] = field(default_factory=list)
    added_results: List[MonitorResult] = field(default_factory=list)
    pre_text: str = ''


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


class Monitor:
    """keyword들이 주어진 text에 등장하는지 확인하고 매치된 정보를 제공한다"""

    def __init__(self, keywords, snippet_window_size=2):
        self.kwtree = AhocorasickWrapper(keywords, allow_substring_match=False)
        self.snippet_window_size = snippet_window_size

    def check(self, text: str) -> MonitorReport:
        matches = self.kwtree.find_all(text)
        results = [MonitorResult(keyword=match.keyword, snippet=match.make_snippet(self.snippet_window_size))
                   for match in matches]
        return MonitorReport(results=results)


class DiffMonitor:
    """Monitor 비슷하지만, 이전에 주어진 text를 참조해서 매치된 text 주변에 변화가 있지 않으면 무시한다"""

    def __init__(self, keywords, snippet_window_size=2):
        self.kwtree = AhocorasickWrapper(keywords)
        self.snippet_window_size = snippet_window_size
        self.pre_text = ""

    def check(self, text: str) -> DiffMonitorReport:
        if text == self.pre_text:
            monitor_report = DiffMonitorReport(pre_text=self.pre_text)
        else:
            monitor_report = self._diff_results(text)
            self.pre_text = text
        return monitor_report

    def _diff_results(self, new_text):
        pre_matches = self.kwtree.find_all(self.pre_text)
        pre_results = [MonitorResult(match.keyword, match.make_snippet(self.snippet_window_size))
                       for match in pre_matches]
        pre_snippet_set = {result.snippet for result in pre_results}

        new_matches = self.kwtree.find_all(new_text)
        new_results = [MonitorResult(match.keyword, match.make_snippet(self.snippet_window_size))
                       for match in new_matches]
        new_snippet_set = {result.snippet for result in new_results}

        removed_results = [result for result in pre_results if result.snippet not in new_snippet_set]
        added_results = [result for result in new_results if result.snippet not in pre_snippet_set]

        return DiffMonitorReport(removed_results, added_results, self.pre_text)
