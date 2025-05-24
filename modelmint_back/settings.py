from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    lambda_labs_api_key: str = Field(
        ...,
        description="Lambda Labs API key for accessing their cloud services",
        env="LAMBDA_LABS_API_KEY",
    )

    synthetic_data_llm_api_key: str = Field(
        ...,
        description="API key for the LLM service used for synthetic data generation",
        env="SYNTHETIC_DATA_LLM_API_KEY",
    )

    synthetic_data_llm_model: str = Field(
        default="gpt-4.1",
        description="LLM model to use for synthetic data generation",
        env="SYNTHETIC_DATA_LLM_MODEL",
    )

    synthetic_data_llm_temperature: float = Field(
        default=0.7,
        description="Temperature setting for synthetic data generation (0.0 to 1.0)",
        env="SYNTHETIC_DATA_LLM_TEMPERATURE",
    )

    supabase_url: str = Field(
        ...,
        description="Supabase URL for accessing the database",
        env="SUPABASE_URL",
    )

    supabase_key: str = Field(
        ...,
        description="Supabase key for accessing the database",
        env="SUPABASE_KEY",
    )

    database_url: str = Field(
        ...,
        description="Database URL for accessing the database",
        env="DATABASE_URL",
    )

    class Config:
        env_file = ".env"


# Create a global settings instance
settings = Settings()
