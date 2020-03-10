from flask import g
from functools import wraps


def login_required(f):
    #限制只有登录用户才能访问
    @wraps(f)
    def wrapper(*args, **kwargs):
        if g.userid:
            return f(*args, **kwargs)
        else:
            return {'message': 'Invalid Token', 'data': None}, 401

    return wrapper
