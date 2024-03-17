import redis
import tool.statusTool as statusTool
from tool.classDb import httpStatus


class RedisDB:
    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)

    def __repr__(self):
        return f'<RedisDB {self.redis_client}>'
    def get(self, key: str=''):
        """从Redis获取用户信息。"""
        data = f"user:{key}"
        user_data = self.redis_client.hgetall(data)
        if not user_data:
            return None
        return user_data  # 直接返回用户数据

    def set(self, key: str='', value: dict={}):
        """将用户信息存储到Redis。"""
        data = f"user:{key}"
        user_data = self.get(key)
        if user_data is None:  # 如果用户不存在
            # 注意：使用hset并传入字典
            self.redis_client.hset(data, mapping=value)
            # 设置过期时间，例如24小时。这一步是可选的。
            self.redis_client.expire(data,statusTool.EXPIRE_TIME)
            return httpStatus(message="存储成功", data={})
        return httpStatus(message="用户已存在", data={}, code=statusTool.statusCode[12001])


    def delete(self, key: str=''):
        """删除用户信息。"""
        data = f"user:{key}"
        if self.get(key) is not None:  # 如果用户存在
            self.redis_client.delete(data)
            return httpStatus(message="删除成功", data={})
        return httpStatus(message="用户未找到,删除失败", data={}, code=statusTool.statusCode[12000])

