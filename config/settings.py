from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    database_url: str

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    loan_duration_days: int = 14

    # Rate limiting
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60

    auth_rate_limit_requests: int = 5
    auth_rate_limit_window_seconds: int = 60

    # Email settings
    smtp_host: str
    smtp_port: int 
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str

    # Scheduler
    overdue_reminder_hour: int = 11
    overdue_reminder_minute: int = 35

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()