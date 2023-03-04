import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__, static_folder='./templates/images')
app.secret_key = 'marimari'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///team.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("apology.html", msg="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("apology.html", msg="must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("apology.html", msg="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("apology.html", msg="must provide username")

        # Ensure password was submitted
        if not password:
            return render_template("apology.html", msg="must provide password")

        if not confirmation:
            return render_template("apology.html", msg="must provide confirmation")

        if password != confirmation:
            return render_template("apology.html", msg="passwords do not match")

        hash = generate_password_hash(password)

        # Ensure username does not exist
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) >= 1:
            return render_template("apology.html", msg="username already exists")

        # Query database for username
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)

        # Remember which user has logged in
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]

        return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/result")
def result():
    # muscles
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


