from recmd.constants import all_articles, user_activity
from recmd.database import get_id, sum_content_and_format


def get_hot_articles(count=8, filter_items=None, filter_user_id=None):
    """
    关于 hot 的评定：
    浏览量等用户交互次数；
    发布时间；
    其作者声望等等。
    由于这部分工作纯属按一定权重排序，因此我没有做，直接随机取出文章返回

    """
    if count < 1:
        count = 1
    result = []

    if filter_items is None:
        filter_items = []
    if filter_user_id is not None:
        filter_items.extend([key for key in user_activity[filter_user_id]])

    for item in all_articles:
        if get_id(item) not in filter_items:
            result.append(sum_content_and_format(item))
            if len(result) == count:
                return result
    return result
