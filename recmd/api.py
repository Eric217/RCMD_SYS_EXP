from flask_restful import Resource, reqparse
from flask_app.output import Output

from .recommend import recommend_by_user_id, recommend_by_query_ls


class RecommendAllAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id', type=int, location='json')
        self.reqparse.add_argument('articles', type=list, location='json')
        super(RecommendAllAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        user_id = args['user_id']
        articles = args['articles']

        if user_id is None and articles is None:
            ans = {'message': '请传入 id 或文章名'}
            return Output.error(ans)
        elif user_id is None:
            ans = recommend_by_query_ls(articles)
            return Output.success(ans)
        elif articles is None:
            ans = recommend_by_user_id(user_id)
            return Output.success(ans)
        else:
            ans = recommend_by_query_ls(articles, user_id)
            return Output.success(ans)


class RecommendSameAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('user_id', type=int, location='json')
        self.reqparse.add_argument('articles', type=list, location='json')
        super(RecommendSameAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        user_id = args['user_id']
        articles = args['articles']

        if user_id is None and articles is None:
            ans = {'message': '请传入 id 或文章名'}
            return Output.error(ans)
        elif user_id is None:
            ans = recommend_by_query_ls(articles)
            return Output.success(ans)
        elif articles is None:
            ans = recommend_by_user_id(user_id)
            return Output.success(ans)
        else:
            ans = recommend_by_query_ls(articles, user_id)
            return Output.success(ans)

