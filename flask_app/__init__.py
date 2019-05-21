from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from recmd.api import RecommendAllAPI, RecommendSameAPI
from flask_cors import *

import default_config

app = Flask(__name__)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
app.config.from_object(default_config)
CORS(app, supports_credentials=True)

db = SQLAlchemy(app)

api = Api(app)
api.add_resource(RecommendAllAPI, '/back/py/api/v1/recommend')
api.add_resource(RecommendSameAPI, '/back/py/api/v1/recommend_same')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

