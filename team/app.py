import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

# Configure application
app = Flask(__name__, static_folder='./static')
app.secret_key = 'marimari'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///team.db")

# セッション
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# インデックスページ
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")

# お気に入り登録ページ
@app.route("/favorite")
@login_required
def favorite():
    user_id = session["user_id"]
    # likegoogle,likeinstagram, likeyoutubeからそのユーザーがお気に入り登録したものを取得
    googleids = db.execute("SELECT google_id FROM likegoogle WHERE user_id = ?", user_id)
    instagramids = db.execute("SELECT instagram_id FROM likeinstagram WHERE user_id = ?", user_id)
    youtubeids = db.execute("SELECT youtube_id FROM likeyoutube WHERE user_id = ?", user_id)

    #それを値のみのリストにする
    googleids_vals = [i.get("google_id") for i in googleids]
    instagramids_vals = [i.get("instagram_id") for i in instagramids]
    youtubeids_vals = [i.get("youtube_id") for i in youtubeids]
    googles = []
    instagrams = []
    youtubes = []
    #それぞれのidsに含まれているもののデータを取得する
    for i in range(len(googleids_vals)):
        g_data = db.execute("SELECT * FROM google WHERE id =?", googleids_vals[i])
        googles += g_data

    for j in range(len(instagramids_vals)):
        i_data = db.execute("SELECT * FROM instagram WHERE id = ?", instagramids_vals[j])
        instagrams += i_data

    for k in range(len(youtubeids_vals)):
        y_data = db.execute("SELECT * FROM youtube WHERE id = ?", youtubeids_vals[k])
        youtubes += y_data

    return render_template("favorite.html", googles=googles, instagrams=instagrams, youtubes=youtubes)

# キーワードページ
@app.route("/keyword", methods=["GET", "POST"])
@login_required
def keyword():
    return render_template("keyword.html")

# 登録
@app.route("/register", methods=["GET", "POST"])
def register():
    # POSTリクエストの時
    if request.method == "POST":
        # 入力された値を確認
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # ユーザーネームの確認
        if not username:
            return render_template("apology.html", msg="must provide username")

        # パスワードの確認
        elif not password:
            return render_template("apology.html", msg="must provide password")

        # 確認用の確認
        elif not confirmation:
            return render_template("apology.html", msg="must provide password again")

        # パスワードと確認用が一致しているか確認
        elif password != confirmation:
            return render_template("apology.html", msg="must provide the same passwords")


        # そのユーザー名が使われていないかチェック
        # ユーザーネームを調べる
        rows = db.execute("SELECT * FROM users WHERE name = ?", username)
        if len(rows) >= 1:
            return render_template("apology.html", msg="the username is already used")

        else:
            # 情報を挿入する
            password_hash = generate_password_hash(password)
            db.execute("INSERT INTO users (name, hash) VALUES(?, ?)", username, password_hash)

            # インデックスページにリダイレクトする
            return redirect("/")

    else:
        return render_template("register.html")

# ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    # セッションを全てクリア
    session.clear()

    # POSTリクエストの時
    if request.method == "POST":
        # ユーザーのインプットを取得
        username = request.form.get("username")
        password = request.form.get("password")

        # 不当な入力なとき
        if not username:
            return render_template("apology.html", msg="must provide username")

        elif not password:
            return render_template("apology.html", msg="must provide password")

        # 入力されたユーザーネームがあることを確認
        rows = db.execute("SELECT * FROM users WHERE name = ?", username)

        # ユーザーネームとパスワードが一致しているか確認
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return render_template("apology.html", msg="invalid username or password")

        # セッションファイルに追加
        session["user_id"] = rows[0]["id"]

        # インデックスページにリダイレクト
        return redirect("/")

    # Getリクエストの時
    else:
        return render_template("login.html")

# ログアウト
@app.route("/logout", methods=["GET"])
def logout():
    # 全てのセッションをクリア
    session.clear()

    # ログインページにリダイレクト
    return redirect("/login")


# 結果表示ページ
@app.route("/result", methods=["GET"])
@login_required
def result():
    user_id = session["user_id"]
    muscle = request.args.get("muscle")

    # Google、Instagram、YouTubeというテーブルから、その筋肉のデータを取得する
    googles = db.execute("SELECT * FROM google WHERE muscle = ?", muscle)
    instagrams = db.execute("SELECT * FROM instagram WHERE muscle = ?", muscle)
    youtubes = db.execute("SELECT * FROM youtube WHERE muscle = ?", muscle)

    # 既にデータベースに追加されているデータを送る
    googleids = db.execute("SELECT google_id FROM likegoogle WHERE user_id = ?", user_id)
    googleids_vals = [i.get("google_id") for i in googleids]
    instagramids = db.execute("SELECT instagram_id FROM likeinstagram WHERE user_id = ?", user_id)
    instagramids_vals = [i.get("instagram_id") for i in instagramids]
    youtubeids = db.execute("SELECT youtube_id FROM likeyoutube WHERE user_id = ?", user_id)
    youtubeids_vals = [i.get("youtube_id") for i in youtubeids]

    return render_template("result.html", googles=googles, instagrams=instagrams, youtubes=youtubes, googleids=googleids_vals, instagramids=instagramids_vals, youtubeids=youtubeids_vals)


@app.route("/likegoogle", methods=["POST", "DELETE"])
def likegoogle():
    user_id =session["user_id"]
    if request.method == "POST":
        post_id = request.form["post_id"]
        db.execute("INSERT INTO likegoogle(user_id, google_id) VALUES(?, ?)", user_id, post_id)
    elif request.method == "DELETE":
        post_id = request.form["post_id"]
        db.execute("DELETE FROM likegoogle WHERE user_id = ? AND google_id = ?", user_id, post_id)
    return "OK"



@app.route("/likeinstagram", methods=["POST", "DELETE"])
def likeinstagram():
    user_id =session["user_id"]
    if request.method == "POST":
        post_id = request.form["post_id"]
        db.execute("INSERT INTO likeinstagram(user_id, instagram_id) VALUES(?, ?)", user_id, post_id)
    elif request.method == "DELETE":
        post_id = request.form["post_id"]
        db.execute("DELETE FROM likeinstagram WHERE user_id = ? AND instagram_id = ?", user_id, post_id)
    return "OK"


@app.route("/likeyoutube", methods=["POST", "DELETE"])
def likeyoutube():
    user_id =session["user_id"]
    if request.method == "POST":
        post_id = request.form["post_id"]
        db.execute("INSERT INTO likeyoutube(user_id, youtube_id) VALUES(?, ?)", user_id, post_id)
    elif request.method == "DELETE":
        post_id = request.form["post_id"]
        db.execute("DELETE FROM likeyoutube WHERE user_id = ? AND youtube_id = ?", user_id, post_id)
    return "OK"