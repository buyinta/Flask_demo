import random
from flask_restful import Resource

from app import redis_client
from utils.constants import SMS_CODE_EXPIRE


class SMSCodeResource(Resource):
    '''获取短信验证码'''

    def get(self,mobile):
        #生成短信验证码
        rand_num='%06d'% random.randint(0,999999)

        #保存验证码
        key='app:code:{}'.format(mobile)
        redis_client.set(key,rand_num,ex=SMS_CODE_EXPIRE)

        #发送短信，可以借助第三平台celery
        print('短信验证码:"mobile":{},"code":{}'.format(mobile,rand_num))

        return {'mobile': 'mobile'}
