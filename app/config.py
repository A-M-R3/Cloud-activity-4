from pydantic_settings import BaseSettings, SettingsConfigDict

class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PSQL_DB_")

    database: str
    username: str
    password: str
    host: str
    port: str

class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str
    port: int
    password: str
    db: int = 0

class MinioSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MINIO_")

    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    secure: bool = False

postgres_settings = PostgresSettings()
redis_settings = RedisSettings()
minio_settings = MinioSettings()

DATABASE_URL = "postgres://{}:{}@{}:{}/{}".format(
    postgres_settings.username,
    postgres_settings.password,
    postgres_settings.host,
    postgres_settings.port,
    postgres_settings.database,
)

models = ["app.authentication.models", "aerich.models"]