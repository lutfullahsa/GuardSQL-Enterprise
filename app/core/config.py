from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GuardSQL Enterprise"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./guardsql.db"
    OPENAI_API_KEY: str | None = None
    MOCK_LLM: bool = True
    DEFAULT_MAX_QUERY_COST: int = 10000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()