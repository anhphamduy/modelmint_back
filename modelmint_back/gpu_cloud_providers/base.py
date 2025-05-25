from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class GPUCloudProvider(ABC):
    """Abstract base class for GPU cloud providers."""

    @abstractmethod
    def __init__(self):
        """Initialize the cloud provider client."""
        pass

    @abstractmethod
    def list_running_instances(self) -> List[Dict[str, Any]]:
        """
        List all running GPU instances.

        Returns:
            List[Dict[str, Any]]: List of running instances with their details
        """
        pass

    @abstractmethod
    def retrieve_instance_details(self, instance_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific instance.

        Args:
            instance_id (str): The unique identifier of the instance

        Returns:
            Dict[str, Any]: Detailed information about the instance
        """
        pass

    @abstractmethod
    def update_instance_details(
        self, instance_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update configuration or details of an existing instance.

        Args:
            instance_id (str): The unique identifier of the instance
            updates (Dict[str, Any]): Dictionary containing the updates to apply

        Returns:
            Dict[str, Any]: Updated instance details
        """
        pass

    @abstractmethod
    def list_available_instance_types(self) -> List[Dict[str, Any]]:
        """
        List all available GPU instance types that can be launched.

        Returns:
            List[Dict[str, Any]]: List of available instance types with their specifications
        """
        pass

    @abstractmethod
    def launch_instance(
        self,
        instance_type: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Launch a new GPU instance.

        Args:
            instance_type (str): The type of instance to launch
            name (Optional[str]): Optional name for the instance
            config (Optional[Dict[str, Any]]): Additional configuration parameters

        Returns:
            Dict[str, Any]: Details of the launched instance
        """
        pass

    @abstractmethod
    def restart_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Restart a running instance.

        Args:
            instance_id (str): The unique identifier of the instance

        Returns:
            Dict[str, Any]: Updated instance details after restart
        """
        pass

    @abstractmethod
    def terminate_instance(self, instance_id: str) -> bool:
        """
        Terminate/delete an instance.

        Args:
            instance_id (str): The unique identifier of the instance

        Returns:
            bool: True if termination was successful, False otherwise
        """
        pass

    @abstractmethod
    def list_ssh_keys(self) -> List[Dict[str, Any]]:
        """
        List all SSH keys associated with the account.

        Returns:
            List[Dict[str, Any]]: List of SSH keys with their details
        """
        pass

    @abstractmethod
    def add_ssh_key(self, name: str, public_key: str) -> Dict[str, Any]:
        """
        Add a new SSH key to the account.

        Args:
            name (str): Name for the SSH key
            public_key (str): The public SSH key content

        Returns:
            Dict[str, Any]: Details of the added SSH key
        """
        pass

    @abstractmethod
    def delete_ssh_key(self, key_id: str) -> bool:
        """
        Delete an SSH key from the account.

        Args:
            key_id (str): The unique identifier of the SSH key

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass
