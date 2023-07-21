import json
import redis
# Redis 서버에 연결합니다. (호스트와 포트는 실제 Redis 서버에 맞게 변경해주세요.)
redis_host = 'localhost'
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)

def save_data_to_redis(key, data, expire):
    """
    Redis에 데이터를 저장하는 함수
    :param key: Redis에 저장할 데이터의 키
    :param data: Redis에 저장할 데이터
    """
    redis_client.set(key, json.dumps(data))
    redis_client.expire(key, expire) # 24시간 동안 데이터 유지

def get_data_from_redis(key, expire):
    """
    Redis에서 데이터를 불러오는 함수
    :param key: Redis에서 불러올 데이터의 키
    :return: 불러온 데이터 (존재하지 않을 경우 None 반환)
    """
    data = redis_client.get(key)
    redis_client.expire(key, expire) # 24시간 동안 데이터 유지
    return data