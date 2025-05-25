import subprocess
from typing import Any, Dict, List, Optional

from modelmint_back import mcp
from modelmint_back.core.settings import settings
from modelmint_back.gpu_cloud_providers import get_provider


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
    file_system_names: Optional[List[str]] = None,
    hostname: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Launch a new GPU instance on the specified cloud provider using the common SSH key.

    Args:
        provider_name (str): Name of the cloud provider
        instance_type (str): The type of instance to launch
        name (Optional[str]): Optional name for the instance
        region_name (Optional[str]): AWS region name
        file_system_names (Optional[List[str]]): List of file system names to mount
        hostname (Optional[str]): Hostname for the instance

    Returns:
        Dict[str, Any]: Details of the launched instance
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)

    config = {}
    if region_name:
        config["region_name"] = region_name
    # Always use the common SSH key
    config["ssh_key_names"] = [settings.common_ssh_key_name]
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
def list_available_instance_types(provider_name: str) -> List[Any]:
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
def setup_machine_basics(
    provider_name: str,
    instance_id: str,
) -> Dict[str, Any]:
    """
    Set up basic development environment and essential packages on a GPU instance using the common SSH key.

    Args:
        provider_name (str): Name of the cloud provider
        instance_id (str): The unique identifier of the instance

    Returns:
        Dict[str, Any]: Setup results and any errors encountered
    """
    provider = get_provider(provider_name, api_key=settings.lambda_labs_api_key)

    # Get instance details to get SSH connection info
    instance_details = provider.retrieve_instance_details(instance_id)

    if not instance_details or instance_details.get("status") != "running":
        return {
            "success": False,
            "error": "Instance is not running or not found",
            "instance_status": (
                instance_details.get("status") if instance_details else "not_found"
            ),
        }

    # Extract connection details
    ip_address = instance_details.get("ip")
    ssh_user = instance_details.get("username", "ubuntu")  # Default to ubuntu

    if not ip_address:
        return {"success": False, "error": "Could not retrieve instance IP address"}

    # Basic setup commands
    setup_commands = [
        "sudo apt-get update -y",
        "sudo apt-get upgrade -y",
        "sudo apt-get install -y curl wget git vim htop tree unzip build-essential",
    ]

    setup_results = {
        "success": True,
        "instance_id": instance_id,
        "ip_address": ip_address,
        "ssh_key_name": settings.common_ssh_key_name,
        "completed_steps": [],
        "failed_steps": [],
    }

    # Execute setup commands via SSH
    for i, command in enumerate(setup_commands):
        try:
            ssh_command = [
                "ssh",
                "-i",
                settings.common_ssh_private_key_path,
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                "-o",
                "ConnectTimeout=30",
                f"{ssh_user}@{ip_address}",
                command,
            ]

            result = subprocess.run(
                ssh_command, capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                setup_results["completed_steps"].append(
                    {"step": i + 1, "command": command, "status": "success"}
                )
            else:
                setup_results["failed_steps"].append(
                    {
                        "step": i + 1,
                        "command": command,
                        "status": "failed",
                        "error": result.stderr.strip(),
                    }
                )

        except Exception as e:
            setup_results["failed_steps"].append(
                {"step": i + 1, "command": command, "status": "error", "error": str(e)}
            )

    # Final status
    setup_results["success"] = len(setup_results["failed_steps"]) == 0
    setup_results["message"] = (
        f"Setup completed. {len(setup_results['completed_steps'])} successful, {len(setup_results['failed_steps'])} failed."
    )

    return setup_results
