from flask import render_template, g
from info.modules.user import user_blu


@user_blu.route("/user_info")
def user_info():
    return render_template("news/user.html", user=g.user.to_dict())
