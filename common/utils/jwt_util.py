import jwt
from flask import current_app


def generate_jwt(payload, secret=None):
    """
    生成jwt
    :param payload: 载荷
    :param expiry: 过期时间
    :param secret: 密钥
    :return: jwt
    """
    # _payload = {'exp': expiry}
    # # 迭代更新_payload，
    # _payload.update(payload)
    if not secret:
        secret = current_app.config['JWT_SECRET']
    token = jwt.encode(payload, secret, algorithm='HS256')
    return token.decode()


def verify_jwt(token, secret=None):
    """
    校验toke
    :param token: jwt token
    :param secret: 密钥
    :return: payload
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']

    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.PyJWTError:
        payload = None
    return payload
