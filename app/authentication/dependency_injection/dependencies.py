from app.authentication.persistence.redis_repository import RedisRepository

redis_repository = RedisRepository()

def get_redis_repository() -> RedisRepository:
    return redis_repository