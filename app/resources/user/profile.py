from flask import g
from flask_restful import Resource
from sqlalchemy.orm import load_only

from models.user import User
from utils.decorators import login_required


class CurrentUserResource(Resource):
    '''个人中心'''
    method_decorators = {'get': [login_required]}

    def get(self):
        # 获取用户ID
        userid = g.userid

        # 查询用户数据
        user = User.query.options(
            load_only(User.id, User.name, User.profile_photo, User.introduction, User.article_count,
                      User.following_count, User.fans_count)).filter(User.id == userid).first()

        return user.to_dict()
