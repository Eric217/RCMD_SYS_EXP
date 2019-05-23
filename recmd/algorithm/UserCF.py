import math

from recmd.constants import db
from recmd.tools import add_and_create, add_or_inc


def get_data():
    uid_ls = db.get_all_user_id()
    dataset = dict()
    for user in uid_ls:
        dataset[user] = dict()
        aid_ls = db.get_user_relative_article_id(user)
        for item_id in aid_ls:
            dataset[user][item_id] = 1

    return dataset


def get_user_similarity(dataset):

    # 构建倒排表
    item_users = dict()
    for u_id, items in dataset.items():
        for item_id in items:
            add_and_create(item_users, item_id, u_id)  # item_users[item_id].add(u)

    # 计算用户相似矩阵
    C = dict()
    N = dict()
    for item_id, users in item_users.items():
        for u in users:
            add_or_inc(N, u)

            for v in users:
                if u == v:
                    continue
                if u not in C:
                    C[u] = dict()
                if v not in C[u]:
                    C[u][v] = 0

                C[u][v] += 1 / math.log(1+len(users))

    for u, related_users in C.items():
        for v, cuv in related_users.items():
            C[u][v] = cuv / math.sqrt(N[u] * N[v])
    return C


class UserIIFRecommender(object):

    K = 8

    def __init__(self):
        data = get_data()
        user_sim_matrix = get_user_similarity(data)

        self.dataset = data
        self.user_sim_mat = user_sim_matrix

    def recommend_by_user(self, user_id):
        rank = dict()
        interacted_items = self.dataset[user_id]
        for v, wuv in sorted(self.user_sim_mat[user_id].items(),
                             key=lambda x: x[1], reverse=True)[0:self.K]:
            for item, rvi in self.dataset[v].items():
                if item in interacted_items:
                    continue
                if item not in rank:
                    rank[item] = 0
                rank[item] += wuv * rvi
        return rank


_recommender = UserIIFRecommender()


def iif_recommend_by_user(user_id, _max=20):
    item_rank = _recommender.recommend_by_user(user_id)
    ranked_ls = sorted(item_rank.items(), key=lambda x: x[1], reverse=True)[0:_max]
    # [(id, rank),()]
    result = []

    return result


if __name__ == '__main__':
    ls = iif_recommend_by_user(1)
    print(ls)

