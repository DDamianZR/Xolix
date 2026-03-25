from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:12345@localhost:5432/proyecto_escom"
    secret_key: str = "super_secret_key_xolix_change_in_production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Uploads
    upload_dir: str = "uploads"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
