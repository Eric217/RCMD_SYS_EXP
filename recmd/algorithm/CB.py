import numpy as np
import jieba

from recmd.constants import ch_stopwords, all_articles, db
from recmd.database import get_content, get_id
from recmd.tools import is_number, add_or_inc, append_no_rep, lg, cosine, try_insert


class Recommender(object):

    def __init__(self):
        stop_list = ch_stopwords
        news_list = all_articles

        article_count = len(news_list)

        all_words = []
        all_tf = []

        for article in news_list:
            _w = ''
            a_tf = {}  # article words with count
            a_total_words = 0  # article total word count (allow repeat)

            for word in jieba.lcut(get_content(article)):
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
                _tf = all_tf[doc][all_words[word]]

                tf_idf[doc][word] = _tf * _idf

        self.stop_list = stop_list
        self.articles = news_list
        self.keywords = all_words
        self.tf_idf = tf_idf

    def calc_user_vec(self, user_id):
        relative_ids = db.get_user_relative_article_id(user_id)
        vec = np.zeros([1, len(self.keywords)])

        docs = []
        for idx, doc in enumerate(self.articles):
            if get_id(doc) in relative_ids:
                docs.append(idx)

        for doc in docs:
            vec += self.tf_idf[doc, 0:]

        return vec[0, 0:], docs

    def recommend_for_user(self, user_id, except_read=True):
        user_vec, relative_docs = self.calc_user_vec(user_id)

        cos_dict = {}
        for doc in range(len(self.articles)):
            if except_read:
                if doc in relative_docs:
                    continue
            doc_vec = self.tf_idf[doc, 0:]
            cos = cosine(doc_vec, user_vec)
            try_insert(cos_dict, doc, cos)

        result = [self.articles[doc] for doc in cos_dict.keys()]
        return result


_recommender = Recommender()


def recommend_by_user(user_id, except_read=True):
    return _recommender.recommend_for_user(user_id, except_read)


if __name__ == "__main__":  # 测试

    user_id = 1

    result = recommend_by_user(user_id)

    print(result)

