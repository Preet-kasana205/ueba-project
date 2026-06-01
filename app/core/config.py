from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ENVIRONMENT: str = "development"

    model_config = {"env_file": ".env"}

settings = Settings()