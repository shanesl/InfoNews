from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

app = Flask(__name__)

# 定义配置类来封装配置信息
class Config:
    DEBUG = True  # 设置调试模式
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/infonews22"  # 数据库连接地址
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪数据库变化
    REDIS_HOST = "127.0.0.1"  # redis的连接地址  将自定义的配置也封装到Config类中
    REDIS_PORT = 6379



# 从对象中加载配置
app.config.from_object(Config)
# 创建msql连接对象
db = SQLAlchemy(app)
# 创建redis连接对象
rs = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


@app.route("/")
def index():
    return "首页"


if __name__ == "__main__":
    app.run()
