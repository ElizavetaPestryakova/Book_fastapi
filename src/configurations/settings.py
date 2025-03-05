from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # for PostgreSQL
    db_host: str
    db_name: str

    algorithm: str
    secret_key: str
    access_token_expire_minutes: int

    db_test_name: str = "book_fastapi_test_db"
    max_connection_count: int = 10

    @property
    def database_url(self) -> str:
        return f"{self.db_host}/{self.db_name}"
    
    @property
    def database_test_url(self) -> str:
        return f"{self.db_host}/{self.db_test_name}"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
