import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__, static_folder='./templates/images')
app.secret_key = 'marimari'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///team.db")

# セッション
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ログインを必須にする
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# インデックスページ
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    return render_template("index.html")

# お気に入り登録ページ
@app.route("/favorite")
@login_required
def favorite():
    user_id = session["user_id"]
    # likegoogleからデータを取得
    googles = db.execute("SELECT * FROM likegoogle WHERE user_id = ?", user_id)

    # likeinstagramからデータを取得
    instagrams = db.execute("SELECT * FROM likeinstagram WHERE user_id = ?", user_id)

    # likeyoutubeからデータを取得
    youtubes = db.execute("SELECT * FROM likeyoutube WHERE user_id = ?", user_id)

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
@app.route("/logout", methods=["GET", "POST"])
def logout():
    # 全てのセッションをクリア
    session.clear()

    # ログインページにリダイレクト
    return render_template("login.html")


# 結果表示ページ
@app.route("/result")
@login_required
def result():
    # 筋肉一覧
    MUSCLES = ["胸鎖乳突筋", "大胸筋", "上腕二頭筋", "前鋸筋", "外腹斜筋", "腹直筋", "内転筋群", "大腿四頭筋", "前脛骨筋", "僧帽筋", "三角筋", "広背筋", "前腕伸筋群", "前腕屈筋群", "下腿三頭筋", "棘下筋", "上腕三頭筋", "脊柱起立筋", "大腿筋", "ハムストリングス"]
    muscle = request.args.get("muscle")
    if muscle not in MUSCLES:
        return render_template("apology.html", msg="そのような筋肉はありません。")

    else:
        # Google、Instagram、YouTubeというテーブルから、その筋肉のデータを取得する
        googles = db.execute("SELECT * FROM google WHERE muscle = ?", muscle)
        instagrams = db.execute("SELECT * FROM instagram WHERE muscle = ?", muscle)
        youtubes = db.execute("SELECT * FROM youtube WHERE muscle = ?", muscle)
        return render_template("result.html", googles=googles, instagrams=instagrams, youtubes=youtubes)

@app.route('/likegoogle/<int:id>', methods=['POST', 'DELETE'])
def toggle_likegoogle(id):
    user_id = session["user_id"]
    if request.method == 'POST':
        db.execute("INSERT INTO likegoogle (user_id, google_id) VALUES(?, ?)", user_id, id)
    elif request.method == 'DELETE':
        db.execute("DELETE FROM likegoogle WHERE user_id = ? AND google_id = ?", user_id, id)
    return '', 204

@app.route('/likeinstagram/<int:id>', methods=['POST', 'DELETE'])
def toggle_likeinstagram(id):
    user_id = session["user_id"]
    if request.method == 'POST':
        db.execute("INSERT INTO likeinstagram (user_id, instagram_id) VALUES(?, ?)", user_id, id)
    elif request.method == 'DELETE':
        db.execute("DELETE FROM likeinstagram WHERE user_id = ? AND instagram_id = ?", user_id, id)
    return '', 204

@app.route('/likeyoutube/<int:id>', methods=['POST', 'DELETE'])
def toggle_likeyoutube(id):
    user_id = session["user_id"]
    if request.method == 'POST':
        db.execute("INSERT INTO likeyoutube (user_id, youtube_id) VALUES(?, ?)", user_id, id)
    elif request.method == 'DELETE':
        db.execute("DELETE FROM likeyoutube WHERE user_id = ? AND youtube_id = ?", user_id, id)
    return '', 204



