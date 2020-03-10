from flask import Blueprint
from flask_restful import Api

from utils.constants import BASE_URL_PRIFIX
from .passport import SMSCodeResource, LoginResource

# 创建蓝图对象
user_bp = Blueprint('user', __name__,url_prefix=BASE_URL_PRIFIX)

# 创建Api对象
user_api = Api(user_bp)

# 设置json包装格式
from utils.output import output_json

user_api.representation('application/json')(output_json)

# 添加类试图
user_api.add_resource(SMSCodeResource, '/sms/codes/<mob:mobile>')
user_api.add_resource(LoginResource, '/authorizations')

