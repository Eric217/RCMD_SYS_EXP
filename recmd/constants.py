from recmd.database import DataBase, get_user_activity
from recmd.tools import get_chinese_stopwords

db = DataBase()

all_articles = db.get_articles()

ch_stopwords = get_chinese_stopwords()

user_activity = get_user_activity(db)
""" {user_id: {item_id: score, }, } """

