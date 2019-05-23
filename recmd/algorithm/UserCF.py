import math

from recmd.constants import db
from recmd.tools import add_and_create


def get_data():
    uid_ls = db.get_all_user_id()
    dataset = dict()
    for user in uid_ls:
        aid_ls = db.get_user_relative_article_id(user)
        dataset[user] = aid_ls
    return dataset


def get_user_similarity(dataset):

    # 构建倒排表
    item_users = dict()
    for u, items in dataset.items():
        for i in items.keys():
            add_and_create(item_users, i, u)

    # 计算用户相似矩阵
    C = dict()
    N = dict()
    for i, users in item_users.items():
        for u in users:
            N[u] += 1
            for v in users:
                if u == v:
                    continue
                C[u][v] += 1 / math.log(1+len(users))

    W = dict()
    for u, related_users in C.items():
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])
    return W


class UserIIFRecommender(object):

    K = 3

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
            for i, rvi in self.dataset[v].items():
                if i in interacted_items:
                    continue
                rank[i] += wuv * rvi
        return rank
