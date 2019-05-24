from flask_restful import Resource, reqparse
from flask_app.output import Output
from recmd.algorithm.cold_start import get_hot_articles
from recmd.algorithm.rcmd_by_item import rcmd_by_item
from recmd.algorithm.rcmd_by_user import rcmd_by_user


class RecommendAllAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id', type=int, location='json')
        self.reqparse.add_argument('existed_id_ls', type=str, location='json')
        super(RecommendAllAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        user_id = args['user_id']
        filter_ids_arg = args['existed_id_ls']
        if len(filter_ids_arg) == 0:
            filter_ids = []
        else:
            filter_ids = [int(num) for num in filter_ids_arg.split()]

        print('主页推荐,参数 - user id:', user_id)

        last_page = False
        if user_id is None or user_id < 0:
            # no user = cold start
            articles = get_hot_articles(filter_items=filter_ids)
            if len(articles) == 0:
                last_page = True

        else:
            articles = rcmd_by_user(user_id, filter_ids)
            if len(articles) == 0:
                # no rcmd, return hot articles
                articles = get_hot_articles(filter_items=filter_ids, filter_user_id=user_id)
                if len(articles) == 0:
                    last_page = True

        data = {'isLastPage': last_page, 'topics': articles}
        return Output.success(data)


class RecommendSameAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id', type=int, location='json')
        self.reqparse.add_argument('article_id', type=int, location='json')
        super(RecommendSameAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        user_id = args['user_id']
        article_id = args['article_id']

        print('单个item推荐,参数 - 当前用户:', user_id, '当前 item:', article_id)

        ans = rcmd_by_item(article_id, user_id)
        return Output.success(ans)

