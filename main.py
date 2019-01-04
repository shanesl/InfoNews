from flask_migrate import MigrateCommand
from flask_script import Manager
from info import create_app

# 创建web 应用
app = create_app("dev")

# 创建管理器
mgr = Manager(app)

# 使用管理器生成迁移命令
mgr.add_command("mc", MigrateCommand)


@mgr.option("-u", dest="username")  # 可以终端使用命令创建超级管理员 python3 main.py create_superuser -u admin -p 123456
@mgr.option("-p", dest="password")   # 将有参函数编程命令
def create_superuser(username, password):
    # 参数校验
    if not all([username,password]):
        app.logger.error("添加管理员参数不足")
        return

    from info.utils.models import User
    from info import db

    # 添加管理员用户  is_admin = True
    user = User()
    user.mobile = username
    user.password = password
    user.nick_name = username
    user.is_admin = True

    # 提交到数据库
    db.session.add(user)

    # 管理员需要知道是否创建成功，所以手动提交予以提示
    try:
        db.session.commit()
    except BaseException as e:
        app.logger.error("添加管理员失败：%s" % e)
        return

    app.logger.info("添加管理员失败")

if __name__ == "__main__":
    mgr.run()
