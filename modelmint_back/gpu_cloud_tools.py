from typing import Any, Dict, List, Optional

from . import mcp
from .gpu_cloud_providers import get_provider
from .settings import settings


@mcp.tool()
def list_gpu_instances(provider_name: str) -> List[Dict[str, Any]]:
    """
    List all running GPU instances for a specific cloud provider.

    Args:
        provider_name (str): Name of the cloud provider (e.g., 'lambda_labs')

    Returns:
        List[Dict[str, Any]]: List of running instances with their details
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.list_running_instances()


@mcp.tool()
def get_instance_details(provider_name: str, instance_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific GPU instance.

    Args:
        provider_name (str): Name of the cloud provider
        instance_id (str): The unique identifier of the instance

    Returns:
        Dict[str, Any]: Detailed information about the instance
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.retrieve_instance_details(instance_id)


@mcp.tool()
def launch_gpu_instance(
    provider_name: str,
    instance_type: str,
    name: Optional[str] = None,
    region_name: Optional[str] = None,
    ssh_key_names: Optional[List[str]] = None,
    file_system_names: Optional[List[str]] = None,
    hostname: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Launch a new GPU instance on the specified cloud provider.

    Args:
        provider_name (str): Name of the cloud provider
        instance_type (str): The type of instance to launch
        name (Optional[str]): Optional name for the instance
        region_name (Optional[str]): AWS region name
        ssh_key_names (Optional[List[str]]): List of SSH key names to use
        file_system_names (Optional[List[str]]): List of file system names to mount
        hostname (Optional[str]): Hostname for the instance

    Returns:
        Dict[str, Any]: Details of the launched instance
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)

    config = {}
    if region_name:
        config["region_name"] = region_name
    if ssh_key_names:
        config["ssh_key_names"] = ssh_key_names
    if file_system_names:
        config["file_system_names"] = file_system_names
    if hostname:
        config["hostname"] = hostname

    return provider.launch_instance(instance_type, name=name, config=config)


@mcp.tool()
def terminate_gpu_instance(provider_name: str, instance_id: str) -> bool:
    """
    Terminate a GPU instance.

    Args:
        provider_name (str): Name of the cloud provider
        instance_id (str): The unique identifier of the instance

    Returns:
        bool: True if termination was successful
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.terminate_instance(instance_id)


@mcp.tool()
def list_available_instance_types(provider_name: str) -> List[Dict[str, Any]]:
    """
    List all available GPU instance types for a specific cloud provider.

    Args:
        provider_name (str): Name of the cloud provider

    Returns:
        List[Dict[str, Any]]: List of available instance types with their specifications
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.list_available_instance_types()


@mcp.tool()
def restart_gpu_instance(provider_name: str, instance_id: str) -> Dict[str, Any]:
    """
    Restart a running GPU instance.

    Args:
        provider_name (str): Name of the cloud provider
        instance_id (str): The unique identifier of the instance

    Returns:
        Dict[str, Any]: Response from the restart operation
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.restart_instance(instance_id)


@mcp.tool()
def list_ssh_keys(provider_name: str) -> List[Dict[str, Any]]:
    """
    List all SSH keys associated with the cloud provider account.

    Args:
        provider_name (str): Name of the cloud provider

    Returns:
        List[Dict[str, Any]]: List of SSH keys with their details
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.list_ssh_keys()


@mcp.tool()
def add_ssh_key(provider_name: str, name: str, public_key: str) -> Dict[str, Any]:
    """
    Add a new SSH key to the cloud provider account.

    Args:
        provider_name (str): Name of the cloud provider
        name (str): Name for the SSH key
        public_key (str): The public SSH key content

    Returns:
        Dict[str, Any]: Details of the added SSH key
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.add_ssh_key(name, public_key)


@mcp.tool()
def delete_ssh_key(provider_name: str, key_id: str) -> bool:
    """
    Delete an SSH key from the cloud provider account.

    Args:
        provider_name (str): Name of the cloud provider
        key_id (str): The unique identifier of the SSH key

    Returns:
        bool: True if deletion was successful
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)
    return provider.delete_ssh_key(key_id)
