from info.home import home_blu
from flask import render_template, current_app, session

from info.utils.models import User


@home_blu.route("/")
def index():
    # 判断用户是否已登录
    user_id =session.get("user_id")
    user = None
    if user_id:  # 已登录
        try:
            user = User.query.get(user_id)
        except BaseException as e:
            current_app.logger.error(e)

    # 用户存在 则用户对象信息专成字典格式存储，否则则为None
    user = user.to_dict() if user else None

    return render_template("index.html",user=user)


# 创建网站图标路由 (浏览器会自动向网站发起/favicon.ico请求，后端只需要实现该路由，并返回图片即可)
@home_blu.route("/favicon.ico")
def favico():
    # flask 中封装了语法send_static_file
    # 可以获取静态文件的内容，封装为响应对象，并根据内容设置content-type
    response = current_app.send_static_file("news/favicon.ico") # 相对路径基于static文件夹

    return response