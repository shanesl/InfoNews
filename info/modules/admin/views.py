# 个人中心
from flask import render_template, request

from info.modules.admin import admin_blu


@admin_blu.route("/login")  # , methods=["GET", "POST"]
def login():
    if request.method == "GET":
        return render_template("admin/login.html")
