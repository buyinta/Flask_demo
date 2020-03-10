from flask import request, g, jsonify
from utils.jwt_util import verify_jwt


def get_userinfo():
    '''获取用户信息'''
    # 获取请求头中的token
    header = request.headers.get('Authorization')

    g.userid = None
    if header and header.startwith('Bearer'):
        # 取出token
        token = header[7:]
        # 校验token
        data = verify_jwt(token)
        if data:  # 校验成功
            g.userid = data.get('userid')
