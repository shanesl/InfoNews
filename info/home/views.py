from info.home import home_blu
from flask import render_template


@home_blu.route("/")
def index():
    return render_template("index.html")
