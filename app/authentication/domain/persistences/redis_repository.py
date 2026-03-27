import redis
from app.authentication.domain.interfaces import TokenRepository
from app.authentication.domain.vos import TokenBO
from app.config import redis_settings

class RedisTokenRepository(TokenRepository):
    def __init__(self):
        self.redis_client = redis.Redis(
            host=redis_settings.host,
            port=redis_settings.port,
            password=redis_settings.password,
            db=redis_settings.db,
            decode_responses=True
        )
        self.token_expiration_seconds = 3600

    async def create(self, token: str, user_id: int) -> TokenBO:
        self.redis_client.setex(name=token, time=self.token_expiration_seconds, value=str(user_id))
        return TokenBO(token=token, user_id=user_id)

    async def get_by_token(self, token: str) -> TokenBO | None:
        user_id_str = self.redis_client.get(name=token)
        if user_id_str:
            return TokenBO(token=token, user_id=int(user_id_str))
        return None

    async def delete(self, token: str) -> None:
        self.redis_client.delete(token)