from datetime import datetime
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from sqlalchemy.orm import load_only

from models import db
from models.article import Article, Collection, Attitude
from models.user import User, Relation
from utils.constants import HOME_PRE_PAGE
from flask import g
from models.article import ArticleContent

"""
首页列表数据分页采用下拉刷新和上拉加载更多方法
"""


class ArticleListResource(Resource):
    def get(self):
        # 获取参数
        parser = RequestParser()
        parser.add_argument('channel_id', required=True, location='args', type=int)
        parser.add_argument('timestamp', required=True, location='args', type=int)
        args = parser.parse_args()
        channel_id = args.channel_id
        timestamp = args.timestamp

        # 如果为"推荐"频道, 先返回空数据
        if channel_id == 0:
            return {'results': [], 'pre_timestamp': 0}

        # timestamp转为datetime类型
        date = datetime.fromtimestamp(timestamp * 0.001)
        # 查询频道中对应的数据  连接查询    要求: 频道对应 & 审核通过 & 发布时间 < timestamp
        data = db.session.query(Article.id, Article.title, Article.user_id, Article.ctime, User.name,
                                Article.comment_count, Article.cover).join(User, Article.user_id == User.id).filter(
            Article.channel_id == channel_id, Article.status == Article.STATUS.APPROVED, Article.ctime < date).order_by(
            Article.ctime.desc()).limit(HOME_PRE_PAGE).all()

        # 序列化
        articles = [{
            'art_id': item.id,
            'title': item.title,
            'aut_id': item.user_id,
            'pubdate': item.ctime.isoformat(),
            'aut_name': item.name,
            'comm_count': item.comment_count,
            'cover': item.cover
        } for item in data]
        # 设置该组数据最后一条的发布时间 为 pre_timestamp
        # 时间对象 转为 时间戳   日期对象.timestamp()
        pre_timestamp = data[-1].ctime.timestamp() * 1000 if data else 0
        # 返回数据
        return {'results': articles, 'pre_timestamp': pre_timestamp}


class ArticleDetailResource(Resource):
    def get(self, article_id):
        # 获取参数
        userid = g.userid

        # 查询基础数据
        data = db.session. \
            query(Article.id, Article.title, Article.ctime, Article.user_id, User.name, User.profile_photo,
                  ArticleContent.content). \
            join(User, Article.user_id == User.id). \
            join(ArticleContent, Article.id == ArticleContent.id). \
            filter(Article.id == article_id).first()

        # 序列化
        article_dict = {
            'art_id': data.id,
            'title': data.title,
            'pubdate': data.ctime.isoformat(),
            'aut_id': data.user_id,
            'aut_name': data.name,
            'aut_photo': data.profile_photo,
            'content': data.content,
            'is_followed': False,
            'attitude': -1,
            'is_collected': False
        }

        '''获取关系数据'''

        # 判断用户是否登录过
        if userid:
            # 查询用户与作者的关系
            relation_obj = Relation.query.options(load_only(Relation.id)).filter(Relation.user_id == userid,
                                                                                 Relation.author_id == data.user_id,
                                                                                 Relation.relation == Relation.RELATION.FOLLOW).first()
            article_dict['is_followed'] = True if relation_obj else False

            # 查询用户的收藏关系  用户 -> 文章    只查询主键即可
            collect_obj = Collection.query.options(load_only(Collection.id)). \
                filter(Collection.user_id == userid, Collection.article_id == article_id,
                       Collection.is_deleted == False).first()

            article_dict['is_collected'] = True if collect_obj else False

            # 查询用户的文章态度  用户 -> 文章
            atti_obj = Attitude.query.options(load_only(Attitude.attitude)). \
                filter(Attitude.user_id == userid, Attitude.article_id == article_id).first()

            article_dict['attitude'] = atti_obj.attitude if atti_obj else -1

        # 返回数据
        return article_dict
