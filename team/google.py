from googleapiclient.discovery import build
from cs50 import SQL
import os
from dotenv import load_dotenv

# definition of database
db = SQL("sqlite:///team.db")

# Get env variables
load_dotenv('.env')

# query engine id
CUSTOM_SEARCH_ENGINE_ID = os.environ.get("CUSTOM_SEARCH_ENGINE_ID")

# API key
API_KEY = os.environ.get("GOOGLE_API_KEY")

# function that get query infomation
def get_search_results(query):

    search = build(
    "customsearch",
    "v1",
    developerKey = API_KEY
)

    result = search.cse().list(
                    q = query,
                    cx = CUSTOM_SEARCH_ENGINE_ID,
                    lr = 'lang_ja',
                    num = 10,
                    start = 1
                ).execute()

    return result


if __name__ == '__main__':
    MUSCLES = ["胸鎖乳突筋", "大胸筋", "上腕二頭筋", "前鋸筋", "外腹斜筋", "腹直筋", "内転筋群", "大腿四頭筋", "前脛骨筋", "僧帽筋", "三角筋", "広背筋", "前腕伸筋群", "前腕屈筋群", "下腿三頭筋", "棘下筋", "上腕三頭筋", "脊柱起立筋", "大腿筋", "ハムストリングス"]

    for muscle in MUSCLES:

        # query keyword
        query = muscle + "　筋トレ"

        # get search results
        result = get_search_results(query)

        # get search results for per parts
        result_items_part = result['items']

        # make a list and dict to save part information
        result_items = []
        item_dict = {}

        # get part info per part
        for i in range(0, 10):
            result_item = result_items_part[i]

            item_dict["title"] = result_item['title']
            item_dict["link"] = result_item['link']
            item_dict["snippet"] = result_item['snippet']

            # append part info into list
            result_items.append(item_dict.copy())

        # add to the database but now this is test
        for result_item in result_items:
            # if the info already exits, not insert
            url = db.execute("SELECT url FROM google WHERE url = ?", result_item["link"])
            if url != None:
                db.execute("INSERT INTO google (url, title, snippet, muscle) VALUES(?, ?, ?, ?)", result_item["link"], result_item["title"], result_item["snippet"], muscle)

            else:
                break

