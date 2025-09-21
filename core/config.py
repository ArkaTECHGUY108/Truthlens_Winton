from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    # ----------------- Google GenAI / Gemini -----------------
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    factcheck_api_key: str = Field(..., alias="FACTCHECK_API_KEY")
    perspective_api_key: str = Field(..., alias="PERSPECTIVE_API_KEY")

    # ----------------- External APIs -----------------
    newsapi_key: Optional[str] = Field(None, alias="NEWSAPI_KEY")
    crowdtangle_api_key: Optional[str] = Field(None, alias="CROWDTANGLE_API_KEY")
    ncri_api_key: Optional[str] = Field(None, alias="NCRI_API_KEY")

    # ----------------- Twitter / X -----------------
    twitter_api_key: Optional[str] = Field(None, alias="TWITTER_API_KEY")
    twitter_api_secret: Optional[str] = Field(None, alias="TWITTER_API_SECRET")
    twitter_bearer: Optional[str] = Field(None, alias="TWITTER_BEARER")
    twitter_access_token: Optional[str] = Field(None, alias="TWITTER_ACCESS_TOKEN")
    twitter_access_secret: Optional[str] = Field(None, alias="TWITTER_ACCESS_SECRET")

    # ----------------- YouTube / Facebook / Instagram -----------------
    youtube_api_key: Optional[str] = Field(None, alias="YOUTUBE_API_KEY")
    facebook_token: Optional[str] = Field(None, alias="FACEBOOK_TOKEN")
    instagram_token: Optional[str] = Field(None, alias="INSTAGRAM_TOKEN")

    # ----------------- Reddit -----------------
    reddit_client_id: str = Field(..., alias="REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(..., alias="REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(..., alias="REDDIT_USER_AGENT")

    # ----------------- Database -----------------
    postgres_user: str = Field(..., alias="POSTGRES_USER")
    postgres_password: str = Field(..., alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(..., alias="POSTGRES_DB")
    postgres_host: str = Field(..., alias="POSTGRES_HOST")
    postgres_port: int = Field(..., alias="POSTGRES_PORT")

    mongo_uri: str = Field(..., alias="MONGO_URI")
    redis_url: str = Field(..., alias="REDIS_URL")

    # ----------------- App Config -----------------
    app_env: str = Field("development", alias="APP_ENV")
    app_port: int = Field(8000, alias="APP_PORT")
    log_level: str = Field("info", alias="LOG_LEVEL")
    secret_key: str = Field(..., alias="SECRET_KEY")

    # ----------------- Validators -----------------
    @field_validator("twitter_bearer", mode="before")
    def warn_if_missing_twitter(cls, v):
        if not v:
            print("⚠️ Warning: Twitter Bearer Token not set. Twitter integration will be limited.")
        return v

    @field_validator("newsapi_key", mode="before")
    def warn_if_missing_newsapi(cls, v):
        if not v:
            print("⚠️ Warning: NEWSAPI_KEY not set. News search will be skipped.")
        return v

    class Config:
        env_file = ".env"
        populate_by_name = True  # ✅ allow alias mapping from uppercase .env
        extra = "ignore"         # ✅ ignore unexpected keys instead of raising errors


# Instantiate settings after class definition
settings = Settings()
