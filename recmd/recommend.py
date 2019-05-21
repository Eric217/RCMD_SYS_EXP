import numpy as np
import jieba
import pymysql
import math
import codecs
import unicodedata
import synonyms as sy
import os

from collections import OrderedDict
from numpy import linalg


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


def get_chinese_stopwords():
    ch_stopwords_filename = os.path.split(os.path.realpath(__file__))[0] + '/stopwords.txt'

    stop_words = []
    for line in codecs.open(ch_stopwords_filename, 'r', 'utf-8'):
        w = line.replace('\n', '')
        if w:
            stop_words.append(w)
    return stop_words


def get_title(obj):
    return obj.get('title')


def get_author_id(obj):
    return obj.get('author').get('id')


class DataBase(object):

    def __init__(self):
        self.connect = pymysql.connect(
            host='localhost',
            port=3306,
            db='intellature',
            user='eric',
            passwd='Eric@12345',
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor()
        self.connect.autocommit(True)

    # count 为需要返回的数目，-1 表示全部
    def get_articles(self, count=-1):
        if count == -1:
            count = 10000000
        query = "select atc.id, atc.author_id, atc.clicks, atc.cover_url, atc.create_time, " \
                "atc.kind_id, atc.likes, atc.title, " \
                "knd.name, acc.username, LEFT(atc.content, 60)" \
                " from t_article as atc, t_kind as knd, t_account as acc" \
                " where atc.kind_id = knd.id and atc.author_id = acc.id" \
                " limit " + pymysql.escape_string(str(count))
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        data = []
        for row in results:
            news = {'id': row[0], 'create_time': row[4], 'title': row[7], 'clicks': row[2],
                    'cover_url': row[3], 'likes': row[6], 'content_summary': row[10],
                    'kind': {'id': row[5], 'name': row[8]},
                    'author': {'id': row[1], 'username': row[9]}}
            data.append(news)
        return data

    def get_article_title(self, author_id=-1):

        if author_id is None or author_id == -1:
            q = "select title from t_article limit 20"
        else:
            a_id = pymysql.escape_string(str(author_id))
            q = '''select title from t_article where id in 
                    (select article_id from t_favorite where user_id =    {}
              union  select article_id from t_like     where account_id = {}
              union  select id         from t_article  where author_id =  {}
              union  select article_id from t_reply    where author_id =  {})
              limit 20 '''.format(a_id, a_id, a_id, a_id)

        self.cursor.execute(q)
        results = self.cursor.fetchall()
        return [row[0] for row in results]

    def __del__(self):
        self.cursor.close()
        self.connect.close()


db = DataBase()

# 300文章，14000 左右关键词，29维，全文检索，cos值 0.82
# 2000文章，7300 左右关键词，144维，仅标题检索，cos值 0.85


def target_dim(data_list):
    d = len(data_list) // 10
    if d == 1 or d == 2:
        d = 3
    elif d == 0:
        d = len(data_list)
    return d


jieba.enable_parallel(4)


def get_fixed_query(origin_query, stop_list):
    """

    :param stop_list: 停用词表
    :param origin_query: 查询串
    :return: 修正后的查询，格式：
    """

    if len(origin_query) == 0:
        # print('输入为空')
        return None
    query_words = []
    for w in jieba.lcut(origin_query):
        if not w or w in stop_list:
            continue
        else:
            query_words.append(w)
    if len(query_words) == 0:
        # print('输入内容没有明显意义')
        return None
    query_words = list(set(query_words))
    fixed_qry = get_fixed_keywords(query_words)

    return fixed_qry


def get_fixed_keywords(query_word_list, min_match=0.78):
    """
    对查询词列表中的每一个词，找其近义词列表，最终返回总列表

    :param query_word_list: 查询词 列表
    :param min_match: 近义词程度，0-1，1 代表不找近义词，取值取决于近义词库
    :return: [[str, str], []] or None
    """
    if len(query_word_list) == 0:
        return None
    if min_match < 0.5:
        min_match = 0.5

    # 可接受的最小近义词相似度，1 代表禁用近义词, 一般不用变
    # min_synonyms = 0.77
    fixed = []
    for w in query_word_list:
        r = []
        if min_match < 1:
            sy_words, sy_scores = sy.nearby(w)
            for i in range(len(sy_words)):
                if sy_scores[i] >= min_match:
                    r.append(sy_words[i])
        if w not in r:
            r.insert(0, w)
        fixed.append(r)
    return fixed


class Recommender(object):

    def __init__(self):
        stop_list = get_chinese_stopwords()

        news_list = db.get_articles(1000)

        # 生成 词-文档 字典记录了每个词出现在哪些文档里
        tf_dict = {}
        curr_news_idx = 0
        for news in news_list:
            for word in jieba.lcut(get_title(news)):
                if not word:
                    continue
                w1 = word.strip()
                if not word or not w1 or is_number(w1) or w1 in stop_list:
                    continue
                elif word in tf_dict:
                    tf_dict[word].append(curr_news_idx)
                else:
                    tf_dict[word] = [curr_news_idx]
            curr_news_idx += 1

        key_words = [k for k in tf_dict.keys()]

        # 得到很大的 词-文档 稀疏矩阵 X
        X = np.zeros([len(key_words), len(news_list)])
        for l, k in enumerate(key_words):
            for doc_id in tf_dict[k]:
                X[l, doc_id] += 1

        # SVD 分解
        U, sigma, V = linalg.svd(X, full_matrices=True)

        # 降维
        target_dimension = target_dim(news_list)
        min_dim = U.shape[1] if U.shape[1] < V.shape[0] else V.shape[0]
        if min_dim < target_dimension:
            target_dimension = min_dim

        Uk = U[0:, 0: target_dimension]
        Vk = V[0: target_dimension, 0:]
        # print('降至维数:\t\t\t', target_dimension)

        # 文档向量列表，一会直接 for in 计算
        news_vectors = []
        for l in range(len(news_list)):
            news_vectors.append(Vk[0:, l])

        self.stop_list = stop_list
        self.key_words = key_words
        self.news_list = news_list
        self._u_k = Uk
        self.news_vectors = news_vectors

    def recommend(self, origin_query_ls, filter_user_id=-1, fix_number=0):
        """
        根据字符串（可由文本摘要返回）的列表，返回有相关性的文章列表，并且匹配的词高亮
        Note: 匹配的词可能是原查询词的近义词，不一定是原词

        :param origin_query_ls: 字符串的列表
        :param fix_number: 返回固定数量，即使没有相关性
        :param filter_user_id: 不推荐这个 id 的文章（如自己的），默认推荐所有
        :return: [(id, '匹配词1 匹配词2', 'title')]
        """
        query = ''
        for q in origin_query_ls:
            query += q

        fixed_query = get_fixed_query(query, self.stop_list)
        print('查询：', fixed_query)

        group_ls = []
        for group in fixed_query:
            # 第 __i 个搜索主干（近义词列表）
            sy_ls = []
            for word in group:
                # 第 _i 个近义词
                idx = -1
                for i in range(len(self.key_words)):
                    if self.key_words[i] == word:
                        idx = i
                        break
                if idx == -1:
                    continue
                keyword_vec = self._u_k[idx, 0:]
                cos_ls = []
                for i in range(len(self.news_list)):
                    cos = cosine(keyword_vec, self.news_vectors[i])
                    if cos and cos > 0.83:
                        # 找到一个合格的词，(以后可能扩展用到 word)，i代表匹配的文章，cos 为余弦值
                        cos_ls.append((word, i, cos))
                sy_ls.append(cos_ls)
            group_ls.append(sy_ls)

        group_dict_ls = []
        for group in group_ls:
            group_part_dict = {}
            for sy_word in group:
                for cos in sy_word:
                    d = cos[1]
                    if d not in group_part_dict:
                        group_part_dict[d] = cos
                    elif group_part_dict[d][2] < cos[2]:
                        group_part_dict[d] = cos

            group_dict_ls.append(group_part_dict)

        result_dict = {}
        for group_dict in group_dict_ls:
            for k in group_dict:
                cos = group_dict[k]
                if k not in result_dict:
                    result_dict[k] = [cos[2], [cos[0]]]
                else:
                    result_dict[k][0] = result_dict[k][0] + cos[2]
                    result_dict[k][1].append(cos[0])
        # print(result_dict)

        # noinspection PyTypeChecker
        final_dict = OrderedDict(
            sorted(result_dict.items(), key=lambda t: t[1][0], reverse=True))

        result_ls = []

        def result_append(_k):
            _news = self.news_list[_k]

            if filter_user_id != -1:
                if filter_user_id == get_author_id(_news):
                    return False
            _m = ''
            if _k in final_dict:
                _matched = final_dict[_k][1]
                _m = ' '.join(_matched)

            # 为了多线程安全，浅复制再加新键值对
            __news = _news.copy()
            __news['matched'] = _m
            result_ls.append(__news)
            return True

        for k in final_dict:
            result_append(k)

        if fix_number == 0:
            if not fixed_query:
                fix_number = 20
            else:
                return result_ls

        curr_num = len(result_ls)
        print('相关文章数：', curr_num, '补足：', fix_number)

        if curr_num > fix_number:
            return result_ls[0:fix_number]
        elif curr_num < fix_number:
            for i in range(len(self.news_list)):  # todo: shuffle
                if i not in final_dict:
                    if not result_append(i):
                        continue
                    curr_num += 1
                    if curr_num == fix_number:
                        break
        return result_ls


_recommender = Recommender()


def convert_datetime(result_ls):

    for r in result_ls:
        r['create_time'] = str(r['create_time'])

    return result_ls


def recommend_by_query_ls(query_ls, filter_user_id=-1, fix_number=10):
    """
    根据字符串的列表，返回与查询有相关性的 文章字典 的列表
    可用作用户搜索文章的接口
    Note: 返回的文章字典中，matched 键对应的是 以空格分割的匹配词 的字符串
    其中匹配的词 可能是原查询中某个词的近义词，不一定是原词

    :param query_ls: list of string
    :param filter_user_id: 不推荐该用户自己的文章，默认推荐所有
    :param fix_number: 返回固定数量结果，即使没有相关性，默认20条，0代表只返回有相关性的结果，有可能返回空

    :return: [ { } ]
    """
    origin_result = _recommender.recommend(query_ls, filter_user_id, fix_number)
    return convert_datetime(origin_result)


def recommend_by_user_id(u_id, filter_self=True, fix_number=10):
    """
    注释同上

    :param u_id:
    :param filter_self: 不推荐自己的文章
    :param fix_number:
    :return:
    """
    q_ls = db.get_article_title(u_id)
    q_ls = q_ls[0:5]

    filter_id = u_id if filter_self else -1

    return recommend_by_query_ls(q_ls, filter_id, fix_number)


if __name__ == "__main__":  # 测试

    q_list = ["测试文章，测试一下"]
    re = recommend_by_query_ls(q_list)
    # re = recommend_by_user_id(0, filter_self=True)

    for i in re:
        print(i)
