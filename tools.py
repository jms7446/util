import os
from urllib.parse import urlsplit, urlunsplit, parse_qs, urljoin


def make_parent_dir(path):
    """make dir of path if not exist"""
    dir_name = os.path.dirname(path)
    os.makedirs(dir_name, exist_ok=True)


def norm_url_query_string_with_keep(url, keep_keys):
    """keep_keys 의 순서대로 query string 을 재배열한다. keep_keys 에 없는 query string 은 제외한다."""
    url_tuple = urlsplit(url)
    query_dict = parse_qs(url_tuple.query)
    qsl = [(k, query_dict.get(k, [''])[0]) for k in keep_keys]
    query = '&'.join(f'{k}={v}' for k, v in qsl)
    url_tuple = url_tuple._replace(query=query)
    return urlunsplit(url_tuple)


def make_abs_url(base_url, url):
    final_url = urljoin(base_url, url)
    split = urlsplit(final_url)._replace(scheme='', netloc='')
    return urlunsplit(split)


def norm_whitespace(text):
    """모든 종류의 연속된 화이트 스페이스를 하나의 공백으로 변환하고, 앞 뒤는 모두 strip 한다"""
    return ' '.join(text.split())


def flat_text_with_sep(texts_list, sep1='\t', sep2='\n'):
    """[['a', 'b'], ['c', 'd']] 와 같은 구조로 된 데이터를 sep 를 사용하여 하나의 문자열로 푼다

    각 내부 문자열은 norm_whitespace 를 사용하여 공백을 정규화한다
    """
    norm_texts_list = [[norm_whitespace(text) for text in texts] for texts in texts_list]
    return sep2.join(sep1.join(texts) for texts in norm_texts_list)
