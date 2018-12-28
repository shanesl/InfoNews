from flask import session
from flask_migrate import MigrateCommand
from flask_script import Manager
from info import create_app

# 创建web 应用
app = create_app("dev")

# 创建管理器
mgr = Manager(app)

# 使用管理器生成迁移命令
mgr.add_command("mc", MigrateCommand)


@app.route("/")
def index():
    session["name"]= "sl"
    return "首页"


if __name__ == "__main__":
    mgr.run()
