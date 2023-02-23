import requests
import json
from cs50 import SQL

# definition of database
db = SQL("sqlite:///team.db")

def basic_info():
    # 初期
    config = dict()
    # アクセストークン
    config["access_token"]         = 'EAAHsGXyOcH4BAGMba1zqqOZBszZCoBftZATq4SZBvb8K92c6XGq8QnqicKkZCwdP08MuGXJQh3g9wLpbStB2lFYMS5Quc1WM1u9j5R7r0cONZBUhCpJVtRsduIkOWXXLtKfypbto1Yd1qLQwtqZBUyhaheISH8gUMBZCe9EAw7cjWMCINrPEyJoN'
    # アプリID
    config["app_id"]               = '541069184757886'
    # アプリシークレット
    config["app_secret"]           = 'bd10f782ec7b256eb80bdfa10be4efaa'
    # インスタグラムビジネスアカウントID
    config['instagram_account_id'] = "17841458117669593"
    # グラフバージョン
    config["version"]              = 'v16.0'
    # graphドメイン
    config["graph_domain"]         = 'https://graph.facebook.com/'
    # エンドポイント
    config["endpoint_base"]        = config["graph_domain"]+config["version"] + '/'
    # 出力
    return config


    # APIリクエスト用の関数
def InstaApiCall(url, params, request_type):

    # リクエスト
    if request_type == 'POST' :
        # POST
        req = requests.post(url,params)
    else :
        # GET
        req = requests.get(url,params)

    # レスポンス
    res = dict()
    res["url"] = url
    res["endpoint_params"]        = params
    res["endpoint_params_pretty"] = json.dumps(params, indent=4)
    res["json_data"]              = json.loads(req.content)
    res["json_data_pretty"]       = json.dumps(res["json_data"], indent=4)

    # 出力
    return res


def get_hashtag_id(hashtag_word):

    """
    ***********************************************************************************
    【APIのエンドポイント】
    https://graph.facebook.com/{graph-api-version}/ig_hashtag_search?user_id={user-id}&q={hashtag-name}&fields={fields}
    ***********************************************************************************
    """
    # リクエスト
    Params = basic_info()                   # リクエストパラメータ
    Params['hashtag_name'] = hashtag_word   # ハッシュタグ情報

    # エンドポイントに送付するパラメータ
    Params['user_id'] = Params['instagram_account_id']  # インスタユーザID
    Params['q'] = Params['hashtag_name']                # ハッシュタグ名
    Params['fields'] = 'id,name'                        # フィールド情報
    url = Params['endpoint_base'] + 'ig_hashtag_search' # エンドポイントURL

    # レスポンス
    response = InstaApiCall(url, Params, 'GET')

    # 戻り値（ハッシュタグID）
    return response['json_data']['data'][0]['id']


def get_hashtag_media_top(params,hashtag_id) :

    """
    ***********************************************************************************
    【APIのエンドポイント】
    https://graph.facebook.com/{graph-api-version}/{ig-hashtag-id}/top_media?user_id={user-id}&fields={fields}
    ***********************************************************************************
    """
    # パラメータ
    Params = dict()
    Params['user_id'] = params['instagram_account_id']
    Params['fields'] = 'id,children,caption,comment_count,like_count,media_type,media_url,permalink'
    Params['access_token'] = params['access_token']

    # エンドポイントURL
    url = params['endpoint_base'] + hashtag_id + '/' + 'top_media'

    return InstaApiCall(url, Params, 'GET')


# 検索したいハッシュタグワードを記述
hashtag_word = '上腕二頭筋トレ'

# 筋肉の名前
muscle = "上腕二頭筋"

# ハッシュタグIDを取得
hashtag_id = get_hashtag_id(hashtag_word)

# パラメータセット
params = basic_info()

# ハッシュタグ情報取得
hashtag_response = get_hashtag_media_top(params,hashtag_id)

for post in hashtag_response['json_data']['data']:
    # 既に登録されていないか、確認
    url = db.execute("SELECT url FROM instagram WHERE url = ?", post["permalink"])
    if url != None:
        db.execute("INSERT INTO instagram (url, caption, media_id, muscle) VALUES(?, ?, ?, ?)", post["permalink"], post["caption"], post["id"], muscle)
    else:
        break


