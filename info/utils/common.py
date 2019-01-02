# 定义过滤器
import functools

from flask import session, current_app, g

from info.utils.models import User



def func_index_convert(index): # index = 4

    index_dict = {1: "first", 2: "second", 3: "third"}

    return index_dict.get(index, "")


# 查询用户数据
def user_login_data(f):  # f=news_detail

    @functools.wraps(f)  # 该装饰器可以让被装饰的函数使用指定函数的名称
    # 如果使用闭包函数的名称来构建函数标记, 会出现标记冲突, 使用functools.wraps可以解决该问题
    def wrappers(*args,**kwargs):
        # 判断用户是否已登录
        user_id = session.get("user_id")
        user = None
        if user_id: # 已登录
            try:
                user = User.query.get(user_id)
            except BaseException as e:
                current_app.logger.error(e)

        g.user = user
        return f(*args,**kwargs)
    return wrappers
