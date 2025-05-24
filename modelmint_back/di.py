import supabase
from dependency_injector import containers, providers
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from .settings import settings


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    config = providers.Configuration()

    synthetic_data_llm_client = providers.Singleton(
        AsyncOpenAI,
        api_key=settings.synthetic_data_llm_api_key,
    )

    supabase_client = providers.Singleton(
        supabase.acreate_client,
        settings.supabase_url,
        settings.supabase_key,
    )

    # Database configuration
    database = providers.Singleton(
        create_async_engine,
        settings.database_url,
        pool_pre_ping=True,
        connect_args={
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        },
    )

    database_session = providers.Factory(
        AsyncSession,
        database,
        expire_on_commit=False,
    )
