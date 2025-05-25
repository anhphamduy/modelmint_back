import logging

from ..gpu_cloud_providers import PROVIDERS, get_provider
from .settings import settings

logger = logging.getLogger(__name__)


def setup_ssh_keys_for_all_providers() -> None:
    """
    Set up the common SSH key for all available cloud provider accounts during server startup.
    """
    logger.info(f"Setting up SSH keys for {len(PROVIDERS)} cloud providers...")

    for provider_name in PROVIDERS.keys():
        logger.info(f"Setting up SSH key for provider: {provider_name}")

        # Get the appropriate API key for the provider
        api_key = None
        if provider_name == "lambda_labs":
            api_key = settings.lambda_labs_api_key
        # Add more provider API keys here as they are added

        if not api_key:
            logger.warning(f"No API key found for provider: {provider_name}")
            continue

        provider = get_provider(provider_name, api_key=api_key)

        # Check if the SSH key already exists
        existing_keys = provider.list_ssh_keys()
        key_exists = any(
            key.get("name") == settings.common_ssh_key_name
            for key in existing_keys.get("data", [])
        )

        if key_exists:
            logger.info(
                f"SSH key '{settings.common_ssh_key_name}' already exists for {provider_name}"
            )
            continue

        # Add the common SSH key to the provider
        provider.add_ssh_key(
            settings.common_ssh_key_name, settings.common_ssh_public_key
        )
        logger.info(f"Successfully added SSH key to {provider_name}")

    logger.info("SSH key setup completed")


def initialize_server() -> None:
    """
    Initialize the server by setting up SSH keys for all cloud providers.
    This function is called during server startup.
    """
    logger.info("Initializing ModelMint server...")

    setup_ssh_keys_for_all_providers()

    logger.info("Server initialization completed successfully")
