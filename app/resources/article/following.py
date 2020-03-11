from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only
from models import db
from models.user import Relation, User
from utils.decorators import login_required


class FollowUserResource(Resource):
    method_decorators = {'post': [login_required]}

    def post(self):
        # 获取参数
        userid = g.userid
        parser = RequestParser()
        parser.add_argument('target', required=True, location='json', type=int)
        args = parser.parse_args()
        target = args.target

        # 查询参数
        relation = Relation.query.options(load_only(Relation.id)).filter(Relation.user_id == userid,
                                                                         Relation.author_id == target).first()
        if relation:
            # 如果存在关系对象，将记录修改为关注
            relation.relation = Relation.RELATION.FOLLOW

        else:
            relation = Relation(user_id=userid, author_id=target, relation=Relation.RELATION.FOLLOW)
            db.session.add(relation)

        # 作者的粉丝数量加一
        User.query.filter(User.id == target).update({'fans_count': User.fans_count + 1})
        # 用户的关注数量加一
        User.query.filter(User.id == userid).update({'following_count': User.following_count + 1})
        db.session.commit()

        return {'target': target}


class UnFollowUserResource(Resource):
    '''取消关注'''
    method_decorators = {'delete': [login_required]}

    def delete(self, target):
        userid = g.userid

        # 更新用户关注表信息
        Relation.query.filter(Relation.user_id == userid, Relation.author_id == target,
                              Relation.relation == Relation.RELATION.FOLLOW).update({'relation': 0})

        # 让作者的粉丝数量-1
        User.query.filter(User.id == target).update({'fans_count': User.fans_count - 1})
        # 让用户的关注数量-1
        User.query.filter(User.id == userid).update({'following_count': User.following_count - 1})

        db.session.commit()
        return {'target': target}
