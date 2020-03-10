from flask import g
from flask_restful import Resource
from sqlalchemy.orm import load_only
from models import db
from models.article import Channel, UserChannel


class UserChannelResource(Resource):
    """用户频道"""

    def get(self):
        # 获取用户信息
        userid = g.userid

        if userid:  # 判断用户已登录, 查询用户频道

            # 查询用户的频道
            channels = Channel.query.options(load_only(Channel.id, Channel.name)).join(UserChannel,
                                                                                       Channel.id == UserChannel.channel_id).filter(
                UserChannel.user_id == userid, UserChannel.is_deleted == False).order_by(UserChannel.sequence).all()

            if len(channels) == 0:  # 用户没有选择频道, 查询默认频道
                channels = Channel.query.options(load_only(Channel.id, Channel.name)).filter(
                    Channel.is_default == True).all()

        else:
            channels = Channel.query.options(load_only(Channel.id, Channel.name)).filter(
                Channel.is_default == True).all()

        # 序列化
        channel_list = [channel.to_dict() for channel in channels]

        # 添加"推荐"频道
        channel_list.insert(0, {'id': 0, 'name': '推荐'})

        #序列化
        channel_list = [channel.to_dict() for channel in channels]

        # 添加"推荐"频道
        channel_list.insert(0, {'id': 0, 'name': '推荐'})
        # 返回数据
        return {'channels': channel_list}