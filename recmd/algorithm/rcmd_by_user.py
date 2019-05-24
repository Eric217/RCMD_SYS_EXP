import time

from recmd.algorithm.CB import cb_recommend_by_user
from recmd.algorithm.ItemCF import iuf_recommend_by_user
from recmd.algorithm.UserCF import iif_recommend_by_user
from recmd.constants import all_articles
from recmd.database import get_id, ids_to_indices, sum_content_and_format


def rcmd_by_user(user_id, filter_items, _max=60):
    max_split = _max // 3
    article_dict_ls = cb_recommend_by_user(user_id, max_split)
    # [article]
    item_id_ls = iuf_recommend_by_user(user_id, max_split)
    # [(id, {weight: w, reason: {id: score}}), ]
    item_id_ls2 = iif_recommend_by_user(user_id, max_split)
    # [(id, rank), ]

    existed_id_ls = [get_id(article) for article in article_dict_ls]

    add_ids = [pair[0] for pair in item_id_ls if pair[0] not in existed_id_ls]
    existed_id_ls.extend(add_ids)

    add_ids2 = [pair[0] for pair in item_id_ls2 if pair[0] not in existed_id_ls]
    add_ids.extend(add_ids2)

    if len(filter_items) > 0:
        add_ids = [i for i in add_ids if i not in filter_items]
        article_dict_ls = [item for item in article_dict_ls if get_id(item) not in filter_items]

    add_indices = ids_to_indices(add_ids, all_articles)
    part2 = [sum_content_and_format(all_articles[idx]) for idx in add_indices]

    article_dict_ls.extend(part2)
    return article_dict_ls



