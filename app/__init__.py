from flask import Flask
from os.path import *
import sys
from redis import StrictRedis

BASE_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, BASE_DIR + '/common')

redis_client = None

from app.settings.config import config_dict
from utils.constants import EXTRA_ENV_COINFIG


def register_extensions(app):
    '''组件初始化'''
    # SQLAlchemy组件初始化
    from models import db
    db.init_app(app)

    # redis组件初始化
    global redis_client
    redis_client = StrictRedis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])

    # 装饰器添加
    from utils.converters import register_converters
    register_converters(app)

    # 添加请求钩子
    from utils.middlewares import get_userinfo
    app.before_request(get_userinfo)


def create_flask_app(type):
    """创建flask应用"""

    # 创建flask应用
    app = Flask(__name__)
    # 根据类型加载配置子类
    config_class = config_dict[type]
    # 先加载默认配置
    app.config.from_object(config_class)
    # 再加载额外配置
    app.config.from_envvar(EXTRA_ENV_COINFIG, silent=True)

    # 返回应用
    return app


def register_bp(app: Flask):
    '''注册蓝图'''
    from app.resources.user import user_bp  # 进行局部导入, 避免组件没有初始化完成
    app.register_blueprint(user_bp)


def create_app(type):
    """创建应用 和 组件初始化"""

    # 创建flask应用
    app = create_flask_app(type)
    # 组件初始化
    register_extensions(app)
    # 注册蓝图
    register_bp(app)
    return app
