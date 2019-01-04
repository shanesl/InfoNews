# 个人中心
from flask import render_template, request, current_app, jsonify, session, redirect, url_for, g

from info.modules.admin import admin_blu
from info.utils.models import User
from info.utils.response_code import RET, error_map


# 后台登录页
@admin_blu.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":

        user_id = session.get("user_id")
        is_admin = session.get("is_admin")
        if user_id and is_admin:
            return redirect(url_for("admin.index"))

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

    # 保存session 数据，实现免密码登录
    session["user_id"] = user.id
    session["is_admin"] = True

    return redirect(url_for("admin.index"))


# 后台首页
@admin_blu.route("/index")
def index():
    # user_id = session.get("user_id")
    # try:
    #     user = User.query.filter_by(id=user_id).first()
    # except BaseException as e:
    #     current_app.logger.error(e)
    #     return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])
    # return render_template("admin/index.html", user=user.to_dict())
    return render_template("admin/index.html", user=g.user.to_dict())


# 后台退出
@admin_blu.route('/logout')
def logout():
    # 删除session 数据
    session.pop("user_id", None)
    session.pop("is_admin", None)

    # 重定向到后台登录
    return redirect(url_for("admin.login"))
