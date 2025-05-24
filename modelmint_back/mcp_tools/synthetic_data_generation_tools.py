import asyncio
import json
from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject

from modelmint_back.settings import settings

from .. import mcp
from ..di import Container


@mcp.tool()
@inject
async def generate_synthetic_data(
    data_schema: Dict[str, Any],
    num_samples: int = 10,
    client=Provide[Container.synthetic_data_llm_client],
    supabase_client=Provide[Container.supabase_client],
) -> List[Dict[str, Any]]:
    """
    Generate synthetic data using LLM API based on a provided schema.

    Args:
        data_schema (Dict[str, Any]): Schema defining the structure of the data to generate.
            Example:
            {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the person"
                    },
                    "age": {
                        "type": "integer",
                        "description": "Age between 18 and 80"
                    },
                    "email": {
                        "type": "string",
                        "description": "Valid email address"
                    }
                },
                "required": ["name", "age", "email"]
            }
        num_samples (int): Number of synthetic samples to generate

    Returns:
        List[Dict[str, Any]]: List of generated synthetic data samples matching the schema
    """
    # Create the function schema for data generation
    function_schema = {
        "type": "function",
        "name": "generate_data_sample",
        "description": "Generate a single synthetic data sample based on the provided schema",
        "parameters": data_schema,
    }

    async def generate_single_sample():
        response = await client.chat.completions.create(
            model=settings.synthetic_data_llm_model,
            temperature=settings.synthetic_data_llm_temperature,
            messages=[
                {
                    "role": "system",
                    "content": "You are a data generation assistant. Generate realistic data that matches the provided schema exactly.",
                },
                {
                    "role": "user",
                    "content": "Generate a synthetic data sample that matches the schema exactly.",
                },
            ],
            functions=[function_schema],
            function_call={"name": "generate_data_sample"},
        )
        data = json.loads(response.choices[0].message.function_call.arguments)
        await supabase_client.table("synthetic_data").insert(data).execute()
        return data

    samples = await asyncio.gather(
        *[generate_single_sample() for _ in range(num_samples)]
    )
    return samples
