import pymysql


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
    # noinspection SqlResolve
    def get_articles(self, count=-1):
        if count == -1:
            count = 10000000
        query = "select atc.id, atc.author_id, atc.clicks, atc.cover_url, atc.create_time, " \
                "atc.kind_id, atc.likes, atc.title, " \
                "knd.name, acc.username, atc.content" \
                " from t_article as atc, t_kind as knd, t_account as acc" \
                " where atc.kind_id = knd.id and atc.author_id = acc.id" \
                " limit " + pymysql.escape_string(str(count))
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        data = []
        for row in results:
            news = {'id': row[0], 'create_time': str(row[4]), 'title': row[7],
                    'clicks': row[2], 'cover_url': row[3], 'likes': row[6], 'content': row[10],
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

    def get_user_relative_article_id(self, user_id):

        u_id = pymysql.escape_string(str(user_id))
        q = '''select id from t_article where id in 
                            (select article_id from t_favorite where user_id =    {}
                      union  select article_id from t_like     where account_id = {}
                      union  select id         from t_article  where author_id =  {}
                      union  select article_id from t_reply    where author_id =  {})
                      limit 20 '''.format(u_id, u_id, u_id, u_id)

        self.cursor.execute(q)
        results = self.cursor.fetchall()
        return [row[0] for row in results]

    def get_all_user_id(self):
        q = 'select id from t_account'
        self.cursor.execute(q)
        results = self.cursor.fetchall()
        return [row[0] for row in results]

    def __del__(self):
        self.cursor.close()
        self.connect.close()


def extract_main(obj):
    return obj.get('content')


def get_id(obj):
    return obj.get('id')


def get_title(obj):
    return obj.get('title')


def get_author_id(obj):
    return obj.get('author').get('id')


def id_to_idx(item_id, article_ls):
    target_idx = -1
    for idx, doc in enumerate(article_ls):
        if get_id(doc) == item_id:
            target_idx = idx
            break
    return target_idx


def ids_to_indices(id_ls, article_ls):
    indices = []
    for idx, article in enumerate(article_ls):
        if get_id(article) in id_ls:
            indices.append(idx)
            if len(id_ls) == len(indices):
                break

    return indices


def sum_content_and_format(obj, _copy=True, _delete=True, _sum_len=60):
    if _copy:
        _a = obj.copy()
    else:
        _a = obj

    # content to summary
    _a['content_summary'] = _a['content'][0:_sum_len]
    if _delete:
        del _a['content']

    # time convert
    _a['create_time'] = str(_a['create_time'])
    return _a


def get_user_activity(db):
    """

    :return: format: {user_id: {item_id: score, }, }
    """
    uid_ls = db.get_all_user_id()
    dataset = dict()
    for user in uid_ls:
        dataset[user] = dict()
        aid_ls = db.get_user_relative_article_id(user)
        for item_id in aid_ls:
            dataset[user][item_id] = 1

    return dataset
