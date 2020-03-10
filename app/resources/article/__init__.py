from flask import Blueprint
from flask_restful import Api

from app.resources.article.articles import ArticleListResource
from utils.constants import BASE_URL_PRIFIX

# 1、创建蓝图对象
article_bp = Blueprint('article', __name__, url_prefix=BASE_URL_PRIFIX)

# 2、创建API组件对象
article_api = Api(article_bp)

# 设置json包装格式
from utils.output import output_json

article_api.representation('application/json')(output_json)



from .channel import AllChannelResource

# 添加类视图
article_api.add_resource(AllChannelResource, '/channels')
article_api.add_resource(ArticleListResource, '/articles')