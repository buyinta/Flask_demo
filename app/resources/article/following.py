from flask import g
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only
from models import db
from models.user import Relation, User
from utils.decorators import login_required


class FollowUserResource(Resource):
    method_decorators = {'post': [login_required], 'get': [login_required]}

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

    def get(self):
        '''获取关注列表'''
        userid = g.userid
        parser = RequestParser()
        parser.add_argument('page', default=1, location='args', type=int)
        parser.add_argument('per_page', default=2, location='args', type=int)
        args = parser.parse_args()
        page = args.page
        per_page = args.per_page

        # 查询用户关注的列表
        pn = User.query.options(load_only(User.id, User.name, User.fans_count, User.profile_photo)).join(
            Relation, User.id == Relation.author_id).filter(Relation.user_id == userid,
                                                            Relation.relation == Relation.RELATION.FOLLOW
                                                            ).order_by(Relation.update_time.desc()).paginate(page,
                                                                                                             per_page,
                                                                                                             error_out=False)

        # 筛选出当前用户所有的关注作者id
        sub_query = db.session.query(Relation.author_id).filter(Relation.user_id == userid,
                                                                Relation.relation == Relation.RELATION.FOLLOW)

        # 筛选出所有与当前用户“交互关联”的粉丝
        fans_list = Relation.query.options(load_only(Relation.user_id)).filter(Relation.author_id == userid,
                                                                               Relation.relation == Relation.RELATION.FOLLOW,
                                                                               Relation.user_id.in_(sub_query)).all()

        author_list = []
        for item in pn.items:
            author_dict = {
                'id': item.id,
                'name': item.name,
                'photo': item.profile_photo,
                'fans_count': item.fans_count,
                'mutual_follow': False
            }

            # 如果该作者也关注了当前用户, 则为互相关注
            for fans in fans_list:
                if item.id == fans.user_id:
                    author_dict['mutual_follow'] = True
                    break

            author_list.append(author_dict)

        return {'results': author_list, 'per_page': per_page, 'page': pn.page, 'total_count': pn.total,
                'pages': pn.pages}


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
