import base64
import os
from datetime import timedelta

from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from flask_session import Session


# 定义配置类来封装配置信息
class Config:
    DEBUG = True  # 设置调试模式
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/infonews22"  # 数据库连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库变化
    REDIS_HOST = "127.0.0.1"  # redis的连接地址  将自定义的配置也封装到Config类中
    REDIS_PORT = 6379
    SESSION_TYPE = "redis"  # 设置session的存储方式 redis 性能好，方便设置过期时间
    SESSION_REDIScover = Redis(host=REDIS_HOST, port=REDIS_PORT)  # 设置Redis连接对象，组件会使用该对象将session数据保存到redis中
    SESSION_USE_SIGNER = True  # 设置sessionid 进行加密
    SECRET_KEY = base64.b64encode(os.urandom(48)).decode()  # 设置session 的随机秘钥
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # 设置session 过期时间 组件默认支持过期时间


# 创建web 应用
app = Flask(__name__)
# 从对象中加载配置
app.config.from_object(Config)
# 创建msql连接对象
db = SQLAlchemy(app)
# 创建redis连接对象
rs = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

# 初始化session存储对象
Session(app)

# 创建管理器
mgr = Manager(app)
# 初始化迁移器
Migrate(app,db)
# 使用管理器生成迁移命令
mgr.add_command("mc",MigrateCommand)

@app.route("/")
def index():
    return "首页"


if __name__ == "__main__":
    mgr.run()
