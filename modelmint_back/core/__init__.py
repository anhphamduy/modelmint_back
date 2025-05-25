"""Core application components including settings, dependency injection, and startup logic."""

from .di import Container
from .settings import settings
from .startup import initialize_server

__all__ = ["settings", "Container", "initialize_server"]
