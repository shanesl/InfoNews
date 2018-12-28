from flask import current_app

from info.home import home_blu
import logging  # python内置的日志模块，日志可以输出到控制台，也可以写入到文件汇总
# flask 中内置（logger）的日志信息也是使用logging模块实现的，但是日志没有保存到文件汇中

# 使用蓝图来注册路由
@home_blu.route("/")
def index():
    # 建立使用flask封装的logging 语法（会显示具体的错误位置）
    # logging.error("出现了错误")
    current_app.logger.error("出现了错误")
    return "首页"
