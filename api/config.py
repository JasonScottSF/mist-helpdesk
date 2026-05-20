from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379"
    secret_key: str = "changeme"
    mist_base: str = "https://api.mist.com"
    session_ttl: int = 28800   # 8 hours
    mfa_ttl: int = 300         # 5 minutes for pending MFA

    class Config:
        env_file = ".env"


settings = Settings()
