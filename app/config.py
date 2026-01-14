from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "NSE Real-Time F&O Scanner"

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # SmartAPI values from .env
    SMARTAPI_KEY: str = Field(..., env="SMARTAPI_KEY")
    SMARTAPI_CLIENT_ID: str = Field(..., env="SMARTAPI_CLIENT_ID")
    SMARTAPI_PIN: str = Field(..., env="SMARTAPI_PIN")
    SMARTAPI_TOTP_SECRET: str = Field(..., env="SMARTAPI_TOTP_SECRET")

    # --- IMPORTANT: lowercase aliases so code works ---
    @property
    def smartapi_key(self):
        return self.SMARTAPI_KEY

    @property
    def smartapi_client_id(self):
        return self.SMARTAPI_CLIENT_ID

    @property
    def smartapi_pin(self):
        return self.SMARTAPI_PIN

    @property
    def smartapi_totp_secret(self):
        return self.SMARTAPI_TOTP_SECRET

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
