from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from flask_session import Session

from config import DevelopmentConfig

# 创建web 应用
app = Flask(__name__)
# 从对象中加载配置
app.config.from_object(DevelopmentConfig)
# 创建msql连接对象
db = SQLAlchemy(app)
# 创建redis连接对象
rs = Redis(host=DevelopmentConfig.REDIS_HOST, port=DevelopmentConfig.REDIS_PORT)

# 初始化session存储对象
Session(app)

# 创建管理器
mgr = Manager(app)
# 初始化迁移器
Migrate(app, db)
# 使用管理器生成迁移命令
mgr.add_command("mc", MigrateCommand)


@app.route("/")
def index():
    return "首页"


if __name__ == "__main__":
    mgr.run()
