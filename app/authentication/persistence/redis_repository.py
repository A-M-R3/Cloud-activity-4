import redis
from app.config import redis_settings

class RedisRepository:
    def __init__(self):
        self.client = redis.Redis(
            host=redis_settings.host,
            port=redis_settings.port,
            password=redis_settings.password,
            db=redis_settings.db,
            decode_responses=True
        )

    def set_token(self, token: str, username: str, expires_in: int = 3600):
        self.client.setex(name=token, time=expires_in, value=username)

    def get_username(self, token: str) -> str | None:
        return self.client.get(token)

    def delete_token(self, token: str):
        self.client.delete(token)