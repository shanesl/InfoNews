# 个人中心

import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, jsonify, session, redirect, url_for, g, abort

from info.modules.admin import admin_blu
from info.utils.constants import ADMIN_USER_PAGE_MAX_COUNT, ADMIN_NEWS_PAGE_MAX_COUNT
from info.utils.models import User, News
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


# 后台用户统计
@admin_blu.route("/user_count")
def user_count():
    # 用户总人数
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except BaseException as e:
        current_app.logger.error(e)
        total_count = 0

    # 月新增人数 注册时间 >= 本月1号0点
    # 获取当前时间的年和月
    t = time.localtime()

    # 构建日期字符串  2019-01-04
    mon_date_str = "%d-%02d-01" % (t.tm_year, t.tm_mon)

    # 转换为日期对象
    mon_date = datetime.strptime(mon_date_str, "%Y-%m-%d")

    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_date).count()
    except BaseException as e:
        current_app.logger.error(e)
        mon_count = 0

    # 日新增人数
    # 构建日期字符串  2019-01-04
    day_date_str = "%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)
    day_date = datetime.strptime(day_date_str,"%Y-%m-%d")
    try:
        day_count = User.query.filter(User.is_admin == False,User.create_time>=day_date).count()
    except BaseException as e:
        current_app.logger.error(e)
        day_count = 0

    # 某日的注册人数  注册时间 >= 当日0点, < 次日0点
    active_count = []
    active_time = []

    for i in range(0, 30):
        begin_date = day_date - timedelta(days=i)  # 当日0点
        end_date = begin_date + timedelta(days=1)  # 次日0点

        try:
            one_day_count = User.query.filter(User.is_admin == False, User.create_time >= begin_date,
                                              User.create_time < end_date).count()

            active_count.append(one_day_count)  # 存放日期对应的注册人数

            # 将日期对象转为日期字符串
            one_day_str = begin_date.strftime("%Y-%m-%d")
            active_time.append(one_day_str)  # 存放日期字符串

        except BaseException as e:
            current_app.logger.error(e)
            one_day_count = 0

    # 日期和注册量倒序
    active_time.reverse()
    active_count.reverse()

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_count": active_count,
        "active_time": active_time
    }

    return render_template("admin/user_count.html", data=data)


# 后台用户列表
@admin_blu.route('/user_list')
def user_list():
    p = request.args.get("p", 1)   # 页数
    # 校验参数
    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 查询当前用户发布的新闻发布时间倒序，分页查询
    try:
        pn = User.query.order_by(User.last_login.desc()).paginate(p, ADMIN_USER_PAGE_MAX_COUNT)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    data = {
        "user_list": [user.to_admin_dict() for user in pn.items],
        "total_page": pn.pages,
        "cur_page": pn.page

    }  # 注意要传递的数据是否正确

    return render_template("admin/user_list.html", data=data)


# 后台新闻审核
@admin_blu.route('/news_review')
def news_review():

    p = request.args.get("p", 1)  # 页数
    keyword = request.args.get("keyword")   # 关键字搜索
    # 校验参数
    try:
        p = int(p)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    filter_list =[]
    if keyword:
        filter_list.append(News.title.contains(keyword))
    # 查询当前用户发布的新闻发布时间倒序，分页查询
    try:
        pn = News.query.filter(*filter_list).order_by(News.create_time.desc()).paginate(p, ADMIN_NEWS_PAGE_MAX_COUNT)
    except BaseException as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=error_map[RET.DBERR])

    data = {
        "news_list": [news.to_review_dict() for news in pn.items],
        "total_page": pn.pages,
        "cur_page": pn.page

    }  # 注意要传递的数据是否正确

    return render_template("admin/news_review.html", data=data)


# 后台新闻审核详情页
@admin_blu.route('/news_review_detail/<int:news_id>',methods=["GET","POST"])
def news_review_detail(news_id):

    # 查询新闻信息
    try:
        news = News.query.get(news_id)
    except BaseException as e:
        current_app.logger.error(e)
        return abort(403)

    if request.method == "GET":
        return render_template("admin/news_review_detail.html",news=news.to_dict())