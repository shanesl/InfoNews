import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, g, render_template
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import Redis

from config import config_dict

# 定义全局变量，记录数据库连接对象，以便其他文件可以使用
db = None  # type:SQLAlchemy
rs = None  # type:Redis

# 封装应用的创建过程， 工厂函数：让外界提供物料，在函数内部封装对象的创建过程
def create_app(config_type):
    config_class = config_dict[config_type]

    # 创建web 应用
    app = Flask(__name__)

    # 从对象中加载配置
    app.config.from_object(config_class)

    # 声明全局变量
    global db, rs
    # 创建msql连接对象
    db = SQLAlchemy(app)
    # 创建redis连接对象
    rs = Redis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT,decode_responses=True)

    # 初始化session存储对象
    Session(app)

    # 注册蓝图对象
    from info.modules.home import home_blu
    # 为了导入错误，对于只使用一次的引用 在使用前导入
    app.register_blueprint(home_blu)
    # 注册蓝图对象
    from info.modules.passport import passport_blu
    # 为了导入错误，对于只使用一次的引用 在使用前导入
    app.register_blueprint(passport_blu)
    from info.modules.news import news_blu
    # 为了导入错误，对于只使用一次的引用 在使用前导入
    app.register_blueprint(news_blu)
    from info.modules.user import user_blu
    app.register_blueprint(user_blu)
    from info.modules.admin import admin_blu
    app.register_blueprint(admin_blu)

    # 初始化迁移器
    Migrate(app, db)

    # 项目关联模型文件   import * 方法不能在函数/方法中使用
    # from info import models
    import info.utils.models

    # 配置日志
    setup_log(config_class.LOGLEVEL)

    # 添加过滤器到应用
    from info.utils.common import func_index_convert
    app.add_template_filter(func_index_convert, "index_convert")

    # 捕获404 错误
    from info.utils.common import user_login_data

    @app.errorhandler(404)
    @user_login_data
    def error_404(e):

        user = g.user.to_dict() if g.user else None
        return render_template("news/404.html", user=user)

    CSRFProtect(app)
    return app


# 配置日志(将flask 内置的日志和自定义的日志 保存到文件中)
def setup_log(log_level):
    # 设置日志的记录等级
    logging.basicConfig(level=log_level)  # 调试debug级

    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(pathname)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象 添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
