# 定义配置类来封装配置信息
import base64
import os
from datetime import timedelta

import logging
from redis import Redis


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
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 设置数据库自动提交(在每次请求结束后, 会自动提交)

# 配置信息子类化
class DevelopmentConfig(Config):  # 开发环境配置信息
    DEBUG = True  # 设置调试模式
    LOGLEVEL = logging.DEBUG
    WTF_CSRF_ENABLED = False # 关闭 CSRF 校验

class ProductionConfig(Config):  # 生产环境配置信息
    DEBUG = False
    LOGLEVEL = logging.ERROR   # 设置日志等级
    WTF_CSRF_ENABLED = True # 开启 CSRF 校验

config_dict = {
    "dev": DevelopmentConfig,
    "pro": ProductionConfig   # 设置日志等级
}
