from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    lambda_labs_api_key: str = Field(
        ...,
        description="Lambda Labs API key for accessing their cloud services",
        env="LAMBDA_LABS_API_KEY",
    )

    class Config:
        env_file = ".env"


# Create a global settings instance
settings = Settings()
