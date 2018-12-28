from info.home import home_blu


# 使用蓝图来注册路由
@home_blu.route("/")
def index():
    return "首页"
