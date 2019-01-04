from flask import Blueprint

from info.utils.common import user_login_data

admin_blu = Blueprint("admin", __name__, url_prefix="/admin")

from .views import *


# 添加蓝图请求钩子： 只会对蓝图注册的路由进行监听
@admin_blu.before_request
@user_login_data
def check_superuser():
    # 确认是是否为管理员登录
    is_admin = session.get("is_admin")
    if not is_admin and not request.url.endswith(url_for("admin.login")):
        # 只要不是管理员访问，且不是访问的管理员登录页则直接跳转到新闻首页
        return redirect(url_for("home.index"))