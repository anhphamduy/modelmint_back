from typing import Dict, Type, Optional
from .base import GPUCloudProvider
from .lambda_labs import LambdaLabsProvider

# Registry of available GPU cloud providers
PROVIDERS: Dict[str, Type[GPUCloudProvider]] = {
    "lambda_labs": LambdaLabsProvider,
}

def get_provider(provider_name: str, **kwargs) -> GPUCloudProvider:
    """
    Get a GPU cloud provider instance by name.
    
    Args:
        provider_name (str): Name of the provider (e.g., 'lambda_labs')
        **kwargs: Additional arguments to pass to the provider constructor
        
    Returns:
        GPUCloudProvider: Instance of the requested provider
        
    Raises:
        ValueError: If the provider name is not supported
    """
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unsupported GPU cloud provider: {provider_name}")
    
    return PROVIDERS[provider_name](**kwargs)

def register_provider(name: str, provider_class: Type[GPUCloudProvider]) -> None:
    """
    Register a new GPU cloud provider.
    
    Args:
        name (str): Name to register the provider under
        provider_class (Type[GPUCloudProvider]): Provider class to register
    """
    PROVIDERS[name] = provider_class
