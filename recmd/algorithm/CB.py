import numpy as np
import jieba
import time

from recmd.constants import ch_stopwords, all_articles, db, user_activity
from recmd.database import extract_main, get_id, sum_content_and_format, id_to_idx
from recmd.tools import is_number, add_or_inc, append_no_rep, lg, cosine, try_insert


jieba.enable_parallel(8)


class CBRecommender(object):

    def __init__(self):
        stop_list = ch_stopwords
        news_list = all_articles

        article_count = len(news_list)

        all_words = []
        all_tf = []
        s = time.time()

        for article in news_list:
            _w = ''
            a_tf = {}  # article words with count
            a_total_words = 0  # article total word count (allow repeat)

            for word in jieba.cut(extract_main(article).split('\n')[0]):
                _w = word.strip()
                if len(_w) == 0 or is_number(_w) or _w in stop_list:
                    continue

                a_total_words += 1
                add_or_inc(a_tf, _w)
                append_no_rep(all_words, _w)

            for word in a_tf:
                a_tf[word] /= a_total_words

            all_tf.append(a_tf)

        all_words_count = len(all_words)

        tf_idf = np.zeros([article_count, all_words_count])

        _tf = 0
        _idf = 0
        for word in range(all_words_count):

            c = 1
            for article in all_tf:
                if word in article:
                    c += 1
            _idf = lg(article_count / c)

            for doc in range(article_count):
                _tf = all_tf[doc].get(all_words[word], 0)
                tf_idf[doc][word] = _tf * _idf
        e = time.time()
        print('cb init:', e-s)
        self.stop_list = stop_list
        self.articles = news_list
        self.keywords = all_words
        self.tf_idf = tf_idf

    def calc_vec(self, item_ids):
        """

        :param item_ids: {item_id: } or [id, ]
        :return: vec, docs=[idx]
        """
        vec = np.zeros([1, len(self.keywords)])

        docs = []
        for idx, doc in enumerate(self.articles):
            if get_id(doc) in item_ids:
                docs.append(idx)

        for doc in docs:
            vec += self.tf_idf[doc, 0:]

        return vec[0, 0:], docs

    def calc_user_vec(self, user_id):
        relative_ids = user_activity[user_id]  # {item_id: score}
        return self.calc_vec(relative_ids)

    def cb_recommend(self, vec, docs, _max):
        s = time.time()
        cos_dict = {}
        for doc in range(0, len(self.articles), 17):
            if doc in docs:
                continue
            doc_vec = self.tf_idf[doc, 0:]
            cos = cosine(doc_vec, vec)
            if cos is None:
                continue
            try_insert(cos_dict, doc, cos, _max)

        _result = [self.articles[doc] for doc in cos_dict.keys()]
        e = time.time()
        print('cb rec for', len(docs), 'docs:', e-s)
        return _result

    def recommend_for_user(self, user_id, _max=20):
        user_vec, relative_docs = self.calc_user_vec(user_id)
        return self.cb_recommend(user_vec, relative_docs, _max)

    def recommend_for_items(self, item_ids, _max=20):
        vec, docs = self.calc_vec(item_ids)
        return self.cb_recommend(vec, docs, _max)


_recommender = CBRecommender()


def cb_recommend_by_user(user_id, _max=20):
    """
    已经规避掉了已经有过行为的文章

    :return: [article]
    """
    _result = _recommender.recommend_for_user(user_id, _max)
    return [sum_content_and_format(_article) for _article in _result]


def cb_recommend_by_items(item_ids, _max=20):
    """
    已经去掉了相同的文章

    :param item_ids: [id, ]
    :param _max: max return num
    """
    _result = _recommender.recommend_for_items(item_ids, _max)
    return [sum_content_and_format(_article) for _article in _result]


if __name__ == "__main__":  # 测试

    # result = cb_recommend_by_user(7)
    # for r in result:
    #     print(r.get('title'))

    result = cb_recommend_by_items([100007])
