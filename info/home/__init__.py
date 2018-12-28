from flask import Blueprint

# 创建蓝图对象
home_blu = Blueprint("home", __name__)

from .views import *