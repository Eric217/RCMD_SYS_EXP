import math

from recmd.constants import user_activity
from recmd.tools import add_or_inc


def get_item_similarity(dataset):
    # dataset format: {user_id: {item_id: score, }, }

    C = dict()
    N = dict()
    for user_id, items in dataset.items():
        for item in items:
            add_or_inc(N, item)

            for item_ in items:
                if item == item_:
                    continue
                if item not in C:
                    C[item] = dict()
                if item_ not in C[item]:
                    C[item][item_] = 0

                C[item][item_] += 1 / math.log(1+len(items))

    for i, related_items in C.items():
        for j, cij in related_items.items():
            C[i][j] = cij / math.sqrt(N[i] * N[j])
    return C


class ItemCFIUFRecommender(object):

    def __init__(self):
        self.dataset = user_activity
        self.item_sim_mat = get_item_similarity(user_activity)

    def recommend_by_user(self, user_id, _k=8):
        rank = dict()
        items = self.dataset[user_id]
        for item_id, score in items.items():
            for id_, weight in sorted(self.item_sim_mat[item_id].items(), key=lambda x: x[1],
                                      reverse=True)[0: _k]:
                if id_ in items:
                    continue
                if id_ not in rank:
                    rank[id_] = dict()
                    rank[id_]['weight'] = 0
                    rank[id_]['reason'] = {}
                rank[id_]['weight'] += score * weight
                rank[id_]['reason'][item_id] = score * weight

        return rank


_recommender = ItemCFIUFRecommender()


def iuf_recommend_by_user(user_id, _max=20):
    """

    :return: [(id: {weight: w, reason: {id: score}}), ]
    """
    ranked_dict = _recommender.recommend_by_user(user_id)

    result = sorted(ranked_dict.items(), key=lambda x: x[1]['weight'], reverse=True)[0: _max]
    return result


if __name__ == "__main__":
    r = iuf_recommend_by_user(1)
    print(r)
