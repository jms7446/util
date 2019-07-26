from dataclasses import dataclass

from ahocorasick import Automaton


class AhocorasickWrapper:
    def __init__(self, keywords, allow_substring_match):
        self.kwtree = Automaton()
        self.allow_substring_match = allow_substring_match
        for keyword in keywords:
            self.kwtree.add_word(keyword, keyword)
        self.kwtree.make_automaton()

    def find_all(self, text):
        ahocorasick_result = self.kwtree.iter(text)
        matches = self._alt_result_format(ahocorasick_result)
        if self.allow_substring_match:
            return matches
        else:
            return self._exclude_substring_match(matches)

    @staticmethod
    def _alt_result_format(ahocorasick_results):
        """ note: pyahocorasick 에서 나오는 end 값은 매칭된 마지막 index python slicing 개념으로 start, end를 만든다. """
        return [(kw, end + 1 - len(kw), end + 1) for end, kw in ahocorasick_results]

    @staticmethod
    def _exclude_substring_match(matches):
        """다름 매칭에 substring으로 포함되는 매칭은 무시한다"""
        matches = sorted(matches, key=lambda x: (x[1], -x[2]))
        non_substring_matches = []
        max_end = 0
        for match in matches:
            if match[2] > max_end:
                non_substring_matches.append(match)
                max_end = match[2]
        return non_substring_matches


@dataclass(frozen=True)
class Match:
    keyword: str
    snippet: str
    index: int = 0


class Matcher:
    """keyword들이 주어진 text에 등장하는지 확인하고 매치된 정보를 제공한다"""

    def __init__(self, keywords, snippet_window_size=2):
        self.keywords = keywords
        self.snippet_window_size = snippet_window_size

    def match(self, text):
        # naive한 구현
        for keyword in self.keywords:
            pass


class StateMatcher:
    """Matcher와 동일한 기능을 하지만, 이전에 주어진 text를 참조해서 매치된 text 주변에 변화가 있지 않으면 무시한다"""
