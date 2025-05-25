from typing import Any, Dict, List, Optional

from huggingface_hub import list_models, list_repo_files, model_info

from modelmint_back import mcp


@mcp.tool()
def search_models(
    query: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Search for models on Hugging Face Hub based on various criteria.

    Args:
        query (str): Search query string
        limit (int): Maximum number of results to return

    Returns:
        List[Dict[str, Any]]: List of matching models with their details
    """

    models = list_models(search=query, limit=limit)

    return [
        {
            "id": model.modelId,
            "name": model.modelId.split("/")[-1],
            "author": model.modelId.split("/")[0],
            "tags": model.tags,
            "downloads": model.downloads,
            "likes": model.likes,
            "task": model.pipeline_tag,
            "library": model.library_name,
        }
        for model in models
    ]


@mcp.tool()
def get_model_details(repo_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific model.

    Args:
        model_id (str): The model ID (e.g., 'bert-base-uncased')

    Returns:
        Dict[str, Any]: Detailed information about the model
    """
    info = model_info(repo_id)

    return info


@mcp.tool()
def list_model_files(
    model_id: str, revision: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all files available for a specific model.

    Args:
        model_id (str): The model ID (e.g., 'bert-base-uncased')
        revision (Optional[str]): Specific revision/branch to list files from

    Returns:
        List[Dict[str, Any]]: List of files with their details
    """
    files = list_repo_files(model_id, revision=revision)

    return files 