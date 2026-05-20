from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = "changeme"
    session_ttl: int = 28800   # 8 hours

    class Config:
        env_file = ".env"


settings = Settings()
