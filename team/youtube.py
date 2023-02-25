from apiclient.discovery import build
import os
from dotenv import load_dotenv
from cs50 import SQL

db = SQL("sqlite:///team.db")

load_dotenv(".env")

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def get_video_info(keyword):
    # search settings
    youtube_query = youtube.search().list(
        part='id,snippet',
        q=keyword,
        type='video',
        maxResults=10,
        order='relevance',
    )

    # execute()で検索を実行
    youtube_response = youtube_query.execute()

    # 検索結果を取得し、リターンする
    return youtube_response.get('items', [])


if __name__ == '__main__':
    MUSCLES = ["胸鎖乳突筋", "大胸筋", "上腕二頭筋", "前鋸筋", "外腹斜筋", "腹直筋", "内転筋群", "大腿四頭筋", "前脛骨筋", "僧帽筋", "三角筋", "広背筋", "前腕伸筋群", "前腕屈筋群", "下腿三頭筋", "棘下筋", "上腕三頭筋", "脊柱起立筋", "大腿筋", "ハムストリングス"]

    for muscle in MUSCLES:
        # キーワードを設定し、検索
        keyword = muscle
        responses = get_video_info(keyword)

        for response in responses:
            video_title = response["snippet"]["title"]
            video_url = "https://www.youtube.com/watch?v=" + response["id"]["videoId"]
            caption = response["snippet"]["description"]
            channel_title = response["snippet"]["channelTitle"]
            channel_url = "https://www.youtube.com/channel/" + response["snippet"]["channelId"]

            url_in_database = db.execute("SELECT videourl FROM youtube WHERE videourl = ?", video_url)
            if url_in_database != None:
                db.execute("INSERT INTO youtube (videourl, videotitle, channelurl, channeltitle, caption, muscle) VALUES(?, ?, ?, ?, ?, ?)", video_url, video_title, channel_url, channel_title, caption, muscle)

            else:
                break






