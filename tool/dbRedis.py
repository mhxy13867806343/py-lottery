import redis
import schedule
import  time
import tool.statusTool as statusTool
from tool.classDb import httpStatus


class RedisDB:

    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=decode_responses)

    def is_running(self):
        try:
            return self.redis_client.ping()
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            return False
    def __repr__(self):
        return f'<RedisDB {self.redis_client}>'
    def get(self, key: str=''):
        """从Redis获取用户信息。"""
        data = f"user:{key}"
        user_data = self.redis_client.hgetall(data)
        if not user_data:
            return None
        return user_data  # 直接返回用户数据

    def set(self, key: str = '', value: dict = {}):
        """将用户信息存储到Redis。"""
        data = f"user:{key}"
        user_data = self.get(key)
        if user_data is None:  # 如果用户不存在
            # 注意：使用hset并传入字典
            self.redis_client.hset(data, mapping=value)
        else:  # 如果用户已存在
            # 更新用户信息
            self.redis_client.hmset(data, value)
        # 设置过期时间，例如24小时。这一步是可选的。
        self.redis_client.expire(data, statusTool.EXPIRE_TIME)
        return httpStatus(message="存储成功", data={})


    def delete(self, key: str=''):
        """删除用户信息。"""
        data = f"user:{key}"
        if self.get(key) is not None:  # 如果用户存在
            self.redis_client.delete(data)
            return httpStatus(message="删除成功", data={})
        return httpStatus(message="用户未找到,删除失败", data={}, code=statusTool.statusCode[12000])

def check_redis():
    redis_db = RedisDB()
    if not redis_db.is_running():
        return httpStatus(message="redis未运行,请运行", data={}, code=statusTool.statusCode[60000])
check_redis()
#
# schedule.every(600).seconds.do(check_redis) # 每隔600秒检查一次 Redis 是否运行
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)