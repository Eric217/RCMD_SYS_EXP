import math
import unicodedata
import codecs
import os


def get_chinese_stopwords():
    ch_stopwords_filename = os.path.split(os.path.realpath(__file__))[0] + '/stopwords.txt'

    stop_words = []
    for line in codecs.open(ch_stopwords_filename, 'r', 'utf-8'):
        w = line.replace('\n', '')
        if w:
            stop_words.append(w)
    return stop_words


def cosine(a, b):
    if len(a) != len(b):
        print('error: cos length')
        return None
    part_up = 0.0
    a_sq = 0.0
    b_sq = 0.0
    for a1, b1 in zip(a,b):
        part_up += a1*b1
        a_sq += a1**2
        b_sq += b1**2
    part_down = math.sqrt(a_sq*b_sq)
    if part_down == 0.0:
        return None
    else:
        return part_up / part_down


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def try_insert(_dict, _key, _value, _max=20):
    _dict[_key] = _value

    if len(_dict) <= _max:
        return

    _min = 1.1
    _min_doc = -1
    for k in _dict:
        if _dict[k] < _min:
            _min_doc = k
            _min = _dict[k]

    del _dict[_min_doc]


def lg(v):
    return math.log10(v)


def add_or_inc(_dict, _key, bottom=1):
    if _key in _dict:
        _dict[_key] += 1
    else:
        _dict[_key] = bottom


def append_no_rep(_ls, _v):
    if _v not in _ls:
        _ls.append(_v)


def add_and_create(_dict, _key, _value):
    if _key not in _dict:
        _dict[_key] = set()
    _dict[_key].add(_value)


ch_stopwords = get_chinese_stopwords()
