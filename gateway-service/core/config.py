from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
    SERVICE_NAME: str = "gateway-service"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    PRODUCT_SERVICE_URL: str = "http://product-service:8000"
    ORDER_SERVICE_URL: str = "http://order-service:8000"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()
