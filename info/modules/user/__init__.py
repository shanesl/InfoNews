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
    if not user:
        # 用户为登录，返回首页 这样会导致个人页面嵌套页面显示首页 出错 所以统一返回403
        return abort(403)