from flask import g, request
from flask_restful import Resource
from sqlalchemy import insert
from sqlalchemy.orm import load_only
from models import db
from models.article import Channel, UserChannel
from utils.decorators import login_required


class UserChannelResource(Resource):
    """用户频道"""
    method_decorators = {'put': [login_required]}

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

        # 序列化
        channel_list = [channel.to_dict() for channel in channels]

        # 添加"推荐"频道
        channel_list.insert(0, {'id': 0, 'name': '推荐'})
        # 返回数据
        return {'channels': channel_list}

    def put(self):
        '''
        修改用户频道
        更新方式采用先重置，后更新
        :return:
        '''
        userid = g.userid
        channels = request.json.get('channels')
        # 重置删除用户频道列表数据
        UserChannel.query.filter(UserChannel.user_id == userid, UserChannel.is_deleted == False).update(
            {'is_deleted': True})

        # 采用批量更新插入的方法
        # 批量插入
        insert_stmt = insert(UserChannel).values(
            [{'user_id': userid, 'channel_id': channel['id'], 'sequence': channel['seq']} for channel in channels])
        # 批量更新
        update_stmt = insert_stmt.on_duplicate_key_update(is_deleted=False, sequence=insert_stmt.inserted.sequence)

        # 执行sql
        db.session.execute(update_stmt)
        # 提交事务
        db.session.commit()
        return {'channels': channels}
