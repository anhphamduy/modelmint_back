from typing import Any, Dict, List, Optional

import httpx

from .base import GPUCloudProvider


class LambdaLabsProvider(GPUCloudProvider):
    """Lambda Labs cloud provider implementation."""

    BASE_URL = "https://cloud.lambda.ai/api/v1"

    def __init__(self, api_key: str):
        """
        Initialize Lambda Labs provider.

        Args:
            api_key (str): Lambda Labs API key
        """
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        self.client = httpx.Client(base_url=self.BASE_URL, headers=self.headers)

    def list_running_instances(self) -> List[Dict[str, Any]]:
        """
        List all running GPU instances from Lambda Labs.

        Returns:
            List[Dict[str, Any]]: List of running instances with their details
        """
        response = self.client.get("/instances")
        response.raise_for_status()
        return response.json()

    def retrieve_instance_details(self, instance_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific Lambda Labs instance.

        Args:
            instance_id (str): The unique identifier of the instance

        Returns:
            Dict[str, Any]: Detailed information about the instance
        """
        response = self.client.get(f"/instances/{instance_id}")
        response.raise_for_status()
        return response.json()

    def update_instance_details(
        self, instance_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update the name of an existing Lambda Labs instance.

        Args:
            instance_id (str): The unique identifier of the instance
            updates (Dict[str, Any]): Dictionary containing the updates to apply.
                Currently only supports updating the 'name' field.
                Name must be between 0 and 64 characters.

        Returns:
            Dict[str, Any]: Updated instance details

        Raises:
            ValueError: If updates contain unsupported fields or invalid name length
            httpx.HTTPError: If the API request fails
        """
        if not updates or "name" not in updates:
            raise ValueError("Updates must contain a 'name' field")

        name = updates["name"]
        if not isinstance(name, str) or len(name) > 64:
            raise ValueError("Name must be a string between 0 and 64 characters")

        response = self.client.post(f"/instances/{instance_id}", json={"name": name})
        response.raise_for_status()
        return response.json()

    def list_available_instance_types(self) -> List[Dict[str, Any]]:
        """
        List all available GPU instance types that can be launched on Lambda Labs.

        Returns:
            List[Dict[str, Any]]: List of available instance types with their specifications.
                Each instance type contains:
                - name: The instance type identifier
                - description: Description of the instance type
                - price_cents_per_hour: Cost per hour in cents
                - specs: Dictionary containing hardware specifications
                    - cpu_count: Number of CPU cores
                    - memory_mib: Memory in MiB
                    - gpu_count: Number of GPUs
                    - gpu_memory_mib: GPU memory in MiB
                    - gpu_name: Name of the GPU model

        Raises:
            httpx.HTTPError: If the API request fails
        """
        response = self.client.get("/instance-types")
        response.raise_for_status()

        instance_types = response.json()

        return instance_types

    def launch_instance(
        self,
        instance_type: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Launch a new GPU instance on Lambda Labs.

        Args:
            instance_type (str): The type of instance to launch (e.g., 'gpu_8x_a100')
            name (Optional[str]): Optional name for the instance
            config (Optional[Dict[str, Any]]): Additional configuration parameters:
                - region_name (str): AWS region name (e.g., 'europe-central-1')
                - ssh_key_names (List[str]): List of SSH key names to use
                - file_system_names (List[str]): List of file system names to mount
                - file_system_mounts (List[Dict]): List of file system mount configurations
                    - mount_point (str): Path where to mount the file system
                    - file_system_id (str): ID of the file system to mount
                - hostname (str): Hostname for the instance
                - image (Dict): Image configuration
                    - id (str): ID of the image to use
                - user_data (str): User data script to run on instance launch
                - tags (List[Dict]): List of tags to apply
                    - key (str): Tag key
                    - value (str): Tag value

        Returns:
            Dict[str, Any]: Details of the launched instance

        Raises:
            ValueError: If required parameters are missing or invalid
            httpx.HTTPError: If the API request fails
        """
        if not config:
            config = {}

        # Validate required fields
        if "region_name" not in config:
            raise ValueError("region_name is required in config")

        # Construct the payload
        payload = {
            "region_name": config["region_name"],
            "instance_type_name": instance_type,
            "ssh_key_names": config.get("ssh_key_names", []),
            "file_system_names": config.get("file_system_names", []),
            "file_system_mounts": config.get("file_system_mounts", []),
            "hostname": config.get("hostname", ""),
            "name": name or "",
            "image": config.get("image", {"id": ""}),
            "user_data": config.get("user_data", ""),
            "tags": config.get("tags", []),
        }

        # Validate payload structure
        if not isinstance(payload["ssh_key_names"], list):
            raise ValueError("ssh_key_names must be a list")
        if not isinstance(payload["file_system_names"], list):
            raise ValueError("file_system_names must be a list")
        if not isinstance(payload["file_system_mounts"], list):
            raise ValueError("file_system_mounts must be a list")
        if not isinstance(payload["tags"], list):
            raise ValueError("tags must be a list")

        # Validate file system mounts structure
        for mount in payload["file_system_mounts"]:
            if not isinstance(mount, dict):
                raise ValueError("file_system_mounts must contain dictionaries")
            if "mount_point" not in mount or "file_system_id" not in mount:
                raise ValueError(
                    "file_system_mounts must contain mount_point and file_system_id"
                )

        # Validate tags structure
        for tag in payload["tags"]:
            if not isinstance(tag, dict):
                raise ValueError("tags must contain dictionaries")
            if "key" not in tag or "value" not in tag:
                raise ValueError("tags must contain key and value")

        response = self.client.post("/instance-operations/launch", json=payload)
        response.raise_for_status()
        return response.json()

    def restart_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Restart a running Lambda Labs instance.

        Args:
            instance_id (str): The unique identifier of the instance to restart

        Returns:
            Dict[str, Any]: Response from the restart operation

        Raises:
            ValueError: If instance_id is invalid
            httpx.HTTPError: If the API request fails
        """
        if not instance_id or not isinstance(instance_id, str):
            raise ValueError("instance_id must be a non-empty string")

        payload = {"instance_ids": [instance_id]}

        response = self.client.post("/instance-operations/restart", json=payload)
        response.raise_for_status()
        return response.json()

    def terminate_instance(self, instance_id: str) -> bool:
        """
        Terminate/delete a Lambda Labs instance.

        Args:
            instance_id (str): The unique identifier of the instance to terminate

        Returns:
            bool: True if termination was successful, False otherwise

        Raises:
            ValueError: If instance_id is invalid
            httpx.HTTPError: If the API request fails
        """
        if not instance_id or not isinstance(instance_id, str):
            raise ValueError("instance_id must be a non-empty string")

        payload = {"instance_ids": [instance_id]}

        response = self.client.post("/instance-operations/terminate", json=payload)
        response.raise_for_status()
        return True

    def list_ssh_keys(self) -> List[Dict[str, Any]]:
        """
        List all SSH keys associated with the Lambda Labs account.

        Returns:
            List[Dict[str, Any]]: List of SSH keys with their details

        Raises:
            httpx.HTTPError: If the API request fails
        """
        response = self.client.get("/ssh-keys")
        response.raise_for_status()
        return response.json()

    def add_ssh_key(self, name: str, public_key: str) -> Dict[str, Any]:
        """
        Add a new SSH key to the Lambda Labs account.

        Args:
            name (str): Name for the SSH key
            public_key (str): The public SSH key content

        Returns:
            Dict[str, Any]: Details of the added SSH key

        Raises:
            ValueError: If name or public_key is invalid
            httpx.HTTPError: If the API request fails
        """
        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        if not public_key or not isinstance(public_key, str):
            raise ValueError("public_key must be a non-empty string")

        payload = {"name": name, "public_key": public_key}

        response = self.client.post("/ssh-keys", json=payload)
        response.raise_for_status()
        return response.json()

    def delete_ssh_key(self, key_id: str) -> bool:
        """
        Delete an SSH key from the Lambda Labs account.

        Args:
            key_id (str): The unique identifier of the SSH key

        Returns:
            bool: True if deletion was successful, False otherwise

        Raises:
            ValueError: If key_id is invalid
            httpx.HTTPError: If the API request fails
        """
        if not key_id or not isinstance(key_id, str):
            raise ValueError("key_id must be a non-empty string")

        response = self.client.delete(f"/ssh-keys/{key_id}")
        response.raise_for_status()
        return True
