import os
import redis


client = redis.Redis.from_url(
    os.environ["REDIS_URI"],
    # 바이트를 가져와 자동으로 문자열 디코딩
    decode_responses=True
)