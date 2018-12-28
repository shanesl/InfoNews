from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

from config import config_dict


# 封装应用的创建过程， 工厂函数：让外界提供物料，在函数内部封装对象的创建过程
def create_app(config_type):
    config_class = config_dict[config_type]
    # 创建web 应用
    app = Flask(__name__)
    # 从对象中加载配置
    app.config.from_object(config_class)
    # 创建msql连接对象
    db = SQLAlchemy(app)
    # 创建redis连接对象
    rs = Redis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)

    # 初始化session存储对象
    Session(app)

    # 初始化迁移器
    Migrate(app, db)

    return app