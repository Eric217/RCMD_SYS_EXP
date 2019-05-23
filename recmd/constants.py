from recmd.database import DataBase
from recmd.tools import get_chinese_stopwords

db = DataBase()

all_articles = db.get_articles()

ch_stopwords = get_chinese_stopwords()
