from googleapiclient.discovery import build
from cs50 import SQL

# definition of database
db = SQL("sqlite:///team.db")

# query engine id
CUSTOM_SEARCH_ENGINE_ID = "e752c5ddf9d8c4302"

# API key
API_KEY = "AIzaSyCwGHZdYNL0TFfiCXOWlBUqfiws1koRRkM"

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

    # query keyword
    query = "上腕二頭筋　筋トレ"

    # name of muscle
    muscle = "上腕二頭筋"

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
            db.execute("INSERT INTO google (url, title, snippet) VALUES(?, ?, ?)", result_item["link"], result_item["title"], result_item["snippet"])

        else:
            break






