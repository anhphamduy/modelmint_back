import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from modelmint_back import mcp
from modelmint_back.core.settings import settings


@mcp.tool()
def train_model_with_llamafactory(
    machine_ips: List[str],
    model_id: str,
    dataset_name: str = "alpaca_en_demo",
    training_type: str = "lora",
    num_epochs: int = 3,
    learning_rate: float = 5e-5,
    batch_size: int = 4,
    gradient_accumulation_steps: int = 4,
    max_length: int = 1024,
    output_dir: str = "saves/trained_model",
    stage: str = "sft",
    template: Optional[str] = None,
    lora_rank: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.1,
    use_flash_attention: bool = True,
    bf16: bool = True,
    save_steps: int = 500,
    logging_steps: int = 10,
    warmup_ratio: float = 0.1,
    lr_scheduler_type: str = "cosine",
    additional_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Train a model using LlamaFactory on remote machines.

    Args:
        machine_ips (List[str]): List of machine IP addresses to run training on
        model_id (str): Model identifier (HuggingFace model name or path)
        dataset_name (str): Name of the dataset to use for training
        training_type (str): Type of training - "lora", "full", or "freeze"
        num_epochs (int): Number of training epochs
        learning_rate (float): Learning rate for training
        batch_size (int): Per-device training batch size
        gradient_accumulation_steps (int): Number of gradient accumulation steps
        max_length (int): Maximum sequence length
        output_dir (str): Output directory for saving model checkpoints
        stage (str): Training stage - "sft", "pt", "rm", "ppo", "dpo", "kto"
        template (Optional[str]): Chat template to use (auto-detected if None)
        lora_rank (int): LoRA rank (only used if training_type is "lora")
        lora_alpha (int): LoRA alpha parameter
        lora_dropout (float): LoRA dropout rate
        use_flash_attention (bool): Whether to use FlashAttention-2
        bf16 (bool): Whether to use bfloat16 precision
        save_steps (int): Save checkpoint every N steps
        logging_steps (int): Log every N steps
        warmup_ratio (float): Warmup ratio for learning rate scheduler
        lr_scheduler_type (str): Type of learning rate scheduler
        additional_config (Optional[Dict[str, Any]]): Additional configuration parameters

    Returns:
        Dict[str, Any]: Training results and status for each machine
    """

    # Validate inputs
    if not machine_ips:
        return {"success": False, "error": "No machine IPs provided"}

    if not model_id:
        return {"success": False, "error": "Model ID is required"}

    # Create training configuration
    config = {
        "model_name_or_path": model_id,
        "stage": stage,
        "do_train": True,
        "finetuning_type": training_type,
        "dataset": dataset_name,
        "cutoff_len": max_length,
        "output_dir": output_dir,
        "overwrite_output_dir": True,
        "per_device_train_batch_size": batch_size,
        "gradient_accumulation_steps": gradient_accumulation_steps,
        "learning_rate": learning_rate,
        "num_train_epochs": num_epochs,
        "lr_scheduler_type": lr_scheduler_type,
        "warmup_ratio": warmup_ratio,
        "bf16": bf16,
        "save_steps": save_steps,
        "logging_steps": logging_steps,
        "plot_loss": True,
        "ddp_timeout": 180000000,
    }

    # Add template if specified
    if template:
        config["template"] = template

    # Add LoRA-specific configuration
    if training_type == "lora":
        config.update(
            {
                "lora_target": "all",
                "lora_rank": lora_rank,
                "lora_alpha": lora_alpha,
                "lora_dropout": lora_dropout,
            }
        )

    # Add FlashAttention configuration
    if use_flash_attention:
        config["flash_attn"] = "fa2"

    # Merge additional configuration
    if additional_config:
        config.update(additional_config)

    results = {
        "success": True,
        "machine_results": {},
        "config_used": config,
        "total_machines": len(machine_ips),
        "successful_machines": 0,
        "failed_machines": 0,
    }

    # Execute training on each machine
    for i, machine_ip in enumerate(machine_ips):
        machine_result = _execute_training_on_machine(
            machine_ip=machine_ip, config=config, machine_index=i
        )

        results["machine_results"][machine_ip] = machine_result

        if machine_result["success"]:
            results["successful_machines"] += 1
        else:
            results["failed_machines"] += 1

    # Update overall success status
    results["success"] = results["successful_machines"] > 0

    return results


def _execute_training_on_machine(
    machine_ip: str, config: Dict[str, Any], machine_index: int
) -> Dict[str, Any]:
    """
    Execute training on a single machine.

    Args:
        machine_ip (str): IP address of the machine
        config (Dict[str, Any]): Training configuration
        machine_index (int): Index of the machine in the list

    Returns:
        Dict[str, Any]: Training result for this machine
    """
    try:
        # Create a unique output directory for this machine
        machine_output_dir = f"{config['output_dir']}_machine_{machine_index}_{machine_ip.replace('.', '_')}"
        machine_config = config.copy()
        machine_config["output_dir"] = machine_output_dir

        # Create temporary YAML config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            # Convert config to YAML format
            yaml_content = _dict_to_yaml(machine_config)
            f.write(yaml_content)
            config_file_path = f.name

        try:
            # Copy config file to remote machine
            remote_config_path = f"/tmp/llamafactory_config_{machine_index}.yaml"
            scp_command = [
                "scp",
                "-i",
                settings.common_ssh_private_key_path,
                "-o",
                "StrictHostKeyChecking=no",
                "-o",
                "UserKnownHostsFile=/dev/null",
                config_file_path,
                f"ubuntu@{machine_ip}:{remote_config_path}",
            ]

            scp_result = subprocess.run(
                scp_command, capture_output=True, text=True, timeout=60
            )

            if scp_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to copy config file: {scp_result.stderr}",
                    "machine_ip": machine_ip,
                    "step": "file_transfer",
                }

            # Execute training command on remote machine
            training_command = (
                f"cd /workspace && llamafactory-cli train {remote_config_path}"
            )

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
                f"ubuntu@{machine_ip}",
                training_command,
            ]

            # Start training process (non-blocking)
            process = subprocess.Popen(
                ssh_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            return {
                "success": True,
                "machine_ip": machine_ip,
                "process_id": process.pid,
                "config_file": remote_config_path,
                "output_dir": machine_output_dir,
                "training_command": training_command,
                "status": "training_started",
                "message": f"Training started successfully on {machine_ip}",
            }

        finally:
            # Clean up temporary config file
            try:
                os.unlink(config_file_path)
            except:
                pass

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "SSH connection timeout",
            "machine_ip": machine_ip,
            "step": "ssh_connection",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "machine_ip": machine_ip,
            "step": "execution",
        }


def _dict_to_yaml(data: Dict[str, Any], indent: int = 0) -> str:
    """
    Convert a dictionary to YAML format string.

    Args:
        data (Dict[str, Any]): Dictionary to convert
        indent (int): Current indentation level

    Returns:
        str: YAML formatted string
    """
    yaml_lines = []
    indent_str = "  " * indent

    for key, value in data.items():
        if isinstance(value, dict):
            yaml_lines.append(f"{indent_str}{key}:")
            yaml_lines.append(_dict_to_yaml(value, indent + 1))
        elif isinstance(value, list):
            yaml_lines.append(f"{indent_str}{key}:")
            for item in value:
                if isinstance(item, dict):
                    yaml_lines.append(f"{indent_str}  -")
                    yaml_lines.append(_dict_to_yaml(item, indent + 2))
                else:
                    yaml_lines.append(f"{indent_str}  - {_format_yaml_value(item)}")
        else:
            yaml_lines.append(f"{indent_str}{key}: {_format_yaml_value(value)}")

    return "\n".join(yaml_lines)


def _format_yaml_value(value: Any) -> str:
    """
    Format a value for YAML output.

    Args:
        value (Any): Value to format

    Returns:
        str: Formatted value
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, str):
        # Quote strings that might be interpreted as other types
        if value.lower() in ["true", "false", "null"] or value.isdigit():
            return f'"{value}"'
        return value
    else:
        return str(value)


@mcp.tool()
def check_training_status(
    machine_ips: List[str], output_dir: str = "saves/trained_model"
) -> Dict[str, Any]:
    """
    Check the training status on remote machines.

    Args:
        machine_ips (List[str]): List of machine IP addresses to check
        output_dir (str): Base output directory used in training

    Returns:
        Dict[str, Any]: Status information for each machine
    """
    results = {
        "success": True,
        "machine_status": {},
        "total_machines": len(machine_ips),
    }

    for i, machine_ip in enumerate(machine_ips):
        machine_output_dir = f"{output_dir}_machine_{i}_{machine_ip.replace('.', '_')}"

        try:
            # Check if training is still running
            check_process_command = "ps aux | grep llamafactory-cli | grep -v grep"

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
                f"ubuntu@{machine_ip}",
                check_process_command,
            ]

            process_result = subprocess.run(
                ssh_command, capture_output=True, text=True, timeout=30
            )

            is_running = (
                process_result.returncode == 0
                and "llamafactory-cli" in process_result.stdout
            )

            # Check for output files
            check_output_command = f"ls -la {machine_output_dir}/ 2>/dev/null || echo 'Directory not found'"

            ssh_command[7] = check_output_command

            output_result = subprocess.run(
                ssh_command, capture_output=True, text=True, timeout=30
            )

            # Check for log files
            check_logs_command = f"tail -n 20 {machine_output_dir}/trainer_log.jsonl 2>/dev/null || echo 'No log file found'"

            ssh_command[7] = check_logs_command

            log_result = subprocess.run(
                ssh_command, capture_output=True, text=True, timeout=30
            )

            results["machine_status"][machine_ip] = {
                "success": True,
                "is_training_running": is_running,
                "output_directory": machine_output_dir,
                "output_files": output_result.stdout.strip(),
                "recent_logs": log_result.stdout.strip(),
                "status": "running" if is_running else "completed_or_stopped",
            }

        except Exception as e:
            results["machine_status"][machine_ip] = {
                "success": False,
                "error": f"Failed to check status: {str(e)}",
                "machine_ip": machine_ip,
            }

    return results


@mcp.tool()
def stop_training(machine_ips: List[str]) -> Dict[str, Any]:
    """
    Stop training processes on remote machines.

    Args:
        machine_ips (List[str]): List of machine IP addresses to stop training on

    Returns:
        Dict[str, Any]: Results of stopping training on each machine
    """
    results = {
        "success": True,
        "machine_results": {},
        "total_machines": len(machine_ips),
        "successful_stops": 0,
        "failed_stops": 0,
    }

    for machine_ip in machine_ips:
        try:
            # Kill llamafactory processes
            kill_command = "pkill -f llamafactory-cli"

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
                f"ubuntu@{machine_ip}",
                kill_command,
            ]

            kill_result = subprocess.run(
                ssh_command, capture_output=True, text=True, timeout=30
            )

            results["machine_results"][machine_ip] = {
                "success": True,
                "message": "Training processes stopped",
                "kill_command_output": kill_result.stdout.strip(),
            }
            results["successful_stops"] += 1

        except Exception as e:
            results["machine_results"][machine_ip] = {
                "success": False,
                "error": f"Failed to stop training: {str(e)}",
            }
            results["failed_stops"] += 1

    results["success"] = results["successful_stops"] > 0

    return results
