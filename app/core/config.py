from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev"),
        extra="ignore",
    )

    app_name: str = "FastAPI Floci Demo"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/dev_db"

    redis_url: str = "redis://redis:6379/0"

    aws_region: str = "us-east-1"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_endpoint_url: str | None = "http://floci:4566"

    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    cognito_client_secret: str = ""

    jwt_issuer: str = ""
    jwt_audience: str = ""

    s3_bucket_name: str = "demo-bucket"

    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/1"

    google_sso_enabled: bool = False
    google_client_id: str = ""
    google_client_secret: str = ""

    apple_sso_enabled: bool = False
    apple_client_id: str = ""
    apple_team_id: str = ""
    apple_key_id: str = ""
    apple_private_key: str = ""

    oauth_state_ttl: int = 600


settings = Settings()
