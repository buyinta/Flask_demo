from datetime import datetime, timedelta

import random
from flask import current_app
from flask_restful import Resource
from flask_restful.inputs import regex
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from models import db
from models.user import User
from utils.jwt_util import generate_jwt
from utils.parser import mobile as mobile_type
from app import redis_client
from utils.constants import SMS_CODE_EXPIRE


class SMSCodeResource(Resource):
    '''获取短信验证码'''

    def get(self, mobile):
        # 生成短信验证码
        rand_num = '%06d' % random.randint(0, 999999)

        # 保存验证码
        key = 'app:code:{}'.format(mobile)
        redis_client.set(key, rand_num, ex=SMS_CODE_EXPIRE)

        # 发送短信，可以借助第三平台celery
        print('短信验证码:"mobile":{},"code":{}'.format(mobile, rand_num))

        return {'mobile': 'mobile'}


class LoginResource(Resource):
    '''注册登录'''

    def post(self):
        # 获取参数
        parser = RequestParser()
        parser.add_argument('mobile', required=True, location='json', type=mobile_type)
        parser.add_argument('code', required=True, location='json', type=regex(r'^\d{6}$'))
        args = parser.parse_args()
        mobile = args.mobile
        code = args.code

        # 校验短信验证码
        key = 'app:code:{}'.format(mobile)
        real_code = redis_client.get(key)

        if not real_code or code != real_code.decode():
            return {'message': 'Invalid Code', 'data': None}, 400

        # 删除验证码
        redis_client.delete(key)

        # 校验成功，查询数据库
        user = User.query.options(load_only(User.id)).filter(User.mobile == mobile).first()

        if user:  # 如果用户存在则更新登录时间
            user.last_login = datetime.now()

        else:  # 如果用户不存在，则创建用户
            user = User(mobile=mobile, name=mobile, last_login=datetime.now())
            db.session.add(user)
        db.session.commit()

        # token = generate_jwt({'userid': user.id},
        #                      expiry=datetime.utcnow() + timedelta(days=current_app.config['JWT_EXPIRE_DAYS']))

        token = generate_jwt({'userid': user.id,
                             'exp': datetime.utcnow() + timedelta(days=current_app.config['JWT_EXPIRE_DAYS'])})

        return {'token': token}, 200
