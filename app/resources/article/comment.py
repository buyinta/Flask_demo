from datetime import datetime
from flask import g
from flask_restful import Resource
from flask_restful.inputs import regex
from flask_restful.reqparse import RequestParser
from models import db
from models.article import Comment, Article
from utils.decorators import login_required


class CommentsResource(Resource):
    method_decorators = {'post': [login_required]}

    def post(self):
        '''发布评论'''
        # 获取参数
        userid = g.userid
        parser = RequestParser()
        parser.add_argument('target', required=True, location='json', type=int)
        parser.add_argument('content', required=True, location='json', type=regex(r'.+'))
        args = parser.parse_args()
        target = args.target
        content = args.content

        # 生成评论记录
        comment = Comment(user_id=userid, article_id=target, content=content, parent_id=0)

        db.session.add(comment)

        # 文章的评论数量加一
        Article.query.filter(Article.id == target).update({'comment_count': Article.comment_count + 1})

        db.session.commit()

        return {'com_id': comment.id, 'target': target}
