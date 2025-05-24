from dependency_injector import containers, providers
from openai import AsyncOpenAI
import supabase

from .settings import settings


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    config = providers.Configuration()

    synthetic_data_llm_client = providers.Singleton(
        AsyncOpenAI,
        api_key=settings.synthetic_data_llm_api_key,
    )

    supabase_client = providers.Singleton(
        supabase.create_client,
        settings.supabase_url,
        settings.supabase_key,
    )
