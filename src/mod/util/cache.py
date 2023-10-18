import json
import redis
from mod.util.logger import logger
import os
# Redis 서버에 연결합니다. (호스트와 포트는 실제 Redis 서버에 맞게 변경해주세요.)
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']
redis_client = redis.Redis(host=redis_host, port=redis_port, db=os.environ['REDIS_DB'])
def save_json_to_redis(key, data, expire = 0):
    """
    Redis에 데이터를 저장하는 함수
    :param key: Redis에 저장할 데이터의 키
    :param data: Redis에 저장할 데이터
    """
    
    logger.info(f"save_json_to_redis {key} {data}")
    redis_client.set(key, json.dumps(data))
    if expire :
        redis_client.expire(key, expire)

def get_json_from_redis(key, expire = 0):
    """
    Redis에서 데이터를 불러오는 함수
    :param key: Redis에서 불러올 데이터의 키
    :return: 불러온 데이터 (존재하지 않을 경우 None 반환)
    """
    data = json.loads(redis_client.get(key))
    logger.info(f"get_json_from_redis {key} {data}")
    if expire :
        redis_client.expire(key, expire)
    return data

def save_str_to_redis(key, str, expire = 0):
    """
    Redis에 데이터를 저장하는 함수
    :param key: Redis에 저장할 데이터의 키
    :param data: Redis에 저장할 데이터
    """
    logger.info(f"save_str_to_redis {key} {str}")
    redis_client.set(key, str)
    if expire :
        redis_client.expire(key, expire)

def get_str_from_redis(key, expire = 0):
    """
    Redis에서 데이터를 불러오는 함수
    :param key: Redis에서 불러올 데이터의 키
    :return: 불러온 데이터 (존재하지 않을 경우 None 반환)
    """
    str = redis_client.get(key)
    
    if expire :
        redis_client.expire(key, expire)
    
    if str :
        logger.info(f"get_str_from_redis {key} {str.decode('utf-8')}")
        return str.decode('utf-8')
    return None