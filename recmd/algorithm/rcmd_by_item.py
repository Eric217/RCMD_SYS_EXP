from recmd.algorithm.CB import cb_recommend_by_items
from recmd.constants import user_activity
from recmd.database import get_id


def filter_user(item_ls, user_id):
    if user_id is None or user_id < 0:
        return item_ls
    item_dict = user_activity[user_id]
    return [obj for obj in item_ls if get_id(obj) not in item_dict]


def rcmd_by_item(item_id, filter_user_id=None, _max=20):
    _result = cb_recommend_by_items([item_id], _max)
    return filter_user(_result, filter_user_id)
