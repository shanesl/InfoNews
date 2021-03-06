from flask import Blueprint, g, redirect, url_for, abort

# 创建蓝图对象
from info.utils.common import user_login_data

user_blu = Blueprint("user", __name__, url_prefix="/user")

from .views import *


# 添加蓝图请求钩子： 只会对蓝图注册的路由进行监听
@user_blu.before_request
@user_login_data
def check_user_login():
    user = g.user
    print(request.url)
    if not user :
        # 用户退出且访问路径是/user/user_info 则跳转到首页
        return redirect(url_for("home.index"))
