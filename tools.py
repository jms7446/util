import logging
import os
import pickle
from contextlib import contextmanager
from urllib.parse import urlsplit, urlunsplit, parse_qs, urljoin


def add_file_name_suffix(file_path, suffix):
    """/dir/name.txt -> /dir/name_suffix.txt로 변환"""
    tokens = file_path.rsplit('.', 1)
    name = tokens[0] + '_' + suffix
    if len(tokens) == 2:
        return f'{name}.{tokens[1]}'
    else:
        return name


def make_parent_dir(path):
    """make dir of path if not exist"""
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)


def norm_url_query_string_with_keep(url, keep_keys):
    """keep_keys 의 순서대로 query string 을 재배열한다. keep_keys 에 없는 query string 은 제외한다."""
    url_tuple = urlsplit(url)
    query_dict = parse_qs(url_tuple.query)
    qsl = [(k, query_dict.get(k, [''])[0]) for k in keep_keys]
    query = '&'.join(f'{k}={v}' for k, v in qsl)
    url_tuple = url_tuple._replace(query=query)
    return urlunsplit(url_tuple)


def make_abs_url(base_url, url=None):
    final_url = urljoin(base_url, url) if url else base_url
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


def do_nothing(*args, **kwargs):
    """호출되어도 아무것도 하지 않는 함수"""


################################################################################
# for db
# reference : https://stackoverflow.com/questions/7499767/temporarily-disable-auto-now-auto-now-add
################################################################################

@contextmanager
def turn_off_auto_now(model, field_name):
    _switch_auto_now(model, field_name, False)
    yield
    _switch_auto_now(model, field_name, True)


def _switch_auto_now(model, field_name, on):
    def switch_auto_now(field):
        field.auto_now = on
    do_to_model(model, field_name, switch_auto_now)


@contextmanager
def turn_off_auto_now_add(model, field_name):
    _switch_auto_now_add(model, field_name, False)
    yield
    _switch_auto_now_add(model, field_name, True)


def _switch_auto_now_add(model, field_name, on):
    def switch_auto_now_add(field):
        field.auto_now_add = on
    do_to_model(model, field_name, switch_auto_now_add)


def do_to_model(model, field_name, func):
    field = model._meta.get_field(field_name)
    func(field)

################################################################################

################################################################################
# 파일에 쓰거나 읽기, 디렉토리를 만들고 파일을 열고 귀찮은 작업 묶음
################################################################################


def pickle_dump(obj, file_path):
    make_parent_dir(file_path)
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def text_write(text, file_path):
    make_parent_dir(file_path)
    with open(file_path, 'w') as f:
        f.write(text)


def text_read(file_path):
    with open(file_path, 'r') as f:
        return f.read()

################################################################################


def is_equal_structured_dict(dic1, dic2, verbose=False):
    """간단하게 dict의 키 구조와 value의 타입이 같은지 확인한다
    권장하는 방법은 아닌 것 같지만, 민감한 체킹 부분이 등장하면 그 때 발전시키기로 한다
    """
    if dic1.keys() != dic2.keys():
        if verbose:
            logging.warning(f'{dic1.keys()} differ {dic2.keys()}')
        return False
    for key in dic1.keys():
        value1 = dic1[key]
        value2 = dic2[key]
        if type(value1) != type(value2):
            if verbose:
                logging.warning(f'key: {key}, type({value1}) differ type({value2})')
            return False
        if isinstance(value1, dict):
            if not is_equal_structured_dict(value1, value2, verbose=verbose):
                return False
    return True
