import os
import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

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
def index():
    return render_template("index.html")


@app.route("/result")
def result():
    # muscles
    MUSCLES = ["胸鎖乳突筋", "大胸筋", "上腕二頭筋", "前鋸筋", "外腹斜筋", "腹直筋", "内転筋群", "大腿四頭筋", "前脛骨筋", "僧帽筋", "三角筋", "広背筋", "前腕伸筋群", "前腕屈筋群", "下腿三頭筋", "棘下筋", "上腕三頭筋", "脊柱起立筋", "大腿筋", "ハムストリングス"]
    muscle = request.args.get("muscle")
    if muscle not in MUSCLES:
        return render_template("apology.html", msg="そのような筋肉はありません。")

    else:
        return render_template("result.html", muscle=muscle)