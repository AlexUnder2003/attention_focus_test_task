from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./attention.db"
    secret: str = "SECRET"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
