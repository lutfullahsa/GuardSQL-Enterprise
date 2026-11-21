from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "GuardSQL-Enterprise"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./guardsql.db"
    OPENAI_API_KEY: str
    DEFAULT_MAX_QUERY_COST: int = 100

    class Config:
        env_file = ".env"

settings = Settings()
