from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'Marketplace Seller'
    api_v1_prefix: str = '/api/v1'
    secret_key: str = 'CHANGE_ME'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 24
    postgres_dsn: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/seller_mvp'
    redis_url: str = 'redis://localhost:6379/0'
    credential_encryption_key: str = 'CHANGE_ME_FERNET_BASE64_KEY'
    frontend_origin: str = 'http://localhost:3000'


settings = Settings()
