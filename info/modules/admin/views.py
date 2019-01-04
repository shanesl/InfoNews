# 个人中心
from flask import render_template, request, current_app, jsonify

from info.modules.admin import admin_blu
from info.utils.models import User
from info.utils.response_code import RET, error_map


@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("admin/login.html")

    # post
    # 获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 校验参数
    if not all([username, password]):
        current_app.logger.error("参数不足")
        return render_template("admin/login.html", errmsg="参数不足")

    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    if not user:
        return render_template("admin/login.html", errmsg="管理员不存在")

    if not user.check_password(password):
        return render_template("admin/login.html", errmsg="密码错误")

    return render_template("admin/index.html", user=user)
