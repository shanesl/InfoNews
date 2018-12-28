from info import rs
from info.home import home_blu


# 使用蓝图来注册路由
@home_blu.route("/")
def index():
    rs.set("name","sl")
    return "首页"
