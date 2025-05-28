import asyncio
import json
from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject

from modelmint_back import mcp
from modelmint_back.core.di import Container
from modelmint_back.core.settings import settings
from modelmint_back.models.synthetic_data_models import (
    RunStatus,
    SyntheticData,
    SyntheticDataRun,
)


@mcp.tool()
async def generate_synthetic_data(
    data_schema: Dict[str, Any],
    num_samples: int = 10,
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
    # Get dependencies from container
    container = Container()
    client = container.synthetic_data_llm_client()
    db_session = container.database_session()

    # Create a new synthetic data run
    run = SyntheticDataRun(
        schema=data_schema, num_samples=num_samples, status=RunStatus.IN_PROGRESS
    )
    db_session.add(run)
    await db_session.flush()

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

        # Create a new synthetic data record
        synthetic_data = SyntheticData(data=data, run_id=run.id)
        db_session.add(synthetic_data)
        return data

    try:
        samples = await asyncio.gather(
            *[generate_single_sample() for _ in range(num_samples)]
        )

        # Update run status to completed
        run.status = RunStatus.COMPLETED
        await db_session.commit()

        return samples
    except Exception as e:
        run.status = RunStatus.FAILED
        await db_session.commit()
        raise e


@mcp.tool()
async def estimate_synthetic_data_cost(
    columns: List[Dict[str, Any]],
    num_samples: int,
) -> Dict[str, Any]:
    """
    Calculate the estimated cost for generating synthetic data based on column specifications.

    Args:
        columns (List[Dict[str, Any]]): List of column specifications with estimated token sizes.
            Example:
            [
                {
                    "name": "full_name",
                    "estimated_tokens": 3
                },
                {
                    "name": "email",
                    "estimated_tokens": 4
                },
                {
                    "name": "bio",
                    "estimated_tokens": 50
                },
                {
                    "name": "age",
                    "estimated_tokens": 1
                }
            ]
        num_samples (int): Number of synthetic data samples to generate

    Returns:
        Dict[str, Any]: Cost estimation breakdown including total cost, token usage, and per-sample cost
    """
    # Get dependencies from container
    container = Container()

    # Calculate token estimates
    total_output_tokens_per_sample = sum(
        col.get("estimated_tokens", 1) for col in columns
    )

    # Estimate input tokens (system prompt + user prompt + function schema)
    base_system_prompt_tokens = 25  # "You are a data generation assistant..."
    base_user_prompt_tokens = 15  # "Generate a synthetic data sample..."

    # Function schema tokens (approximate)
    function_schema_tokens = 50  # Base function definition
    for col in columns:
        # Add tokens for each column definition in schema (just property name)
        function_schema_tokens += 5  # Property name

    total_input_tokens_per_sample = (
        base_system_prompt_tokens + base_user_prompt_tokens + function_schema_tokens
    )

    # Total tokens for all samples
    total_input_tokens = total_input_tokens_per_sample * num_samples
    total_output_tokens = total_output_tokens_per_sample * num_samples

    # Get pricing from settings (assuming these exist or use defaults)
    try:
        input_token_cost = getattr(
            settings, "synthetic_data_input_token_cost", 0.0015 / 1000
        )  # Default: $0.0015 per 1K tokens
        output_token_cost = getattr(
            settings, "synthetic_data_output_token_cost", 0.002 / 1000
        )  # Default: $0.002 per 1K tokens
    except:
        # Fallback pricing (OpenAI GPT-4 pricing as example)
        input_token_cost = 0.0015 / 1000
        output_token_cost = 0.002 / 1000

    # Calculate costs
    input_cost = total_input_tokens * input_token_cost
    output_cost = total_output_tokens * output_token_cost
    total_cost = input_cost + output_cost

    # Calculate per-sample breakdown
    cost_per_sample = total_cost / num_samples if num_samples > 0 else 0

    return {
        "total_estimated_cost": round(total_cost, 6),
        "cost_breakdown": {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
        },
        "per_sample": {
            "cost": round(cost_per_sample, 6),
            "input_tokens": total_input_tokens_per_sample,
            "output_tokens": total_output_tokens_per_sample,
        },
        "pricing_rates": {
            "input_token_cost_per_1k": input_token_cost * 1000,
            "output_token_cost_per_1k": output_token_cost * 1000,
        },
        "column_breakdown": [
            {
                "name": col["name"],
                "estimated_tokens": col.get("estimated_tokens", 1),
                "total_tokens_for_all_samples": col.get("estimated_tokens", 1)
                * num_samples,
                "estimated_cost": col.get("estimated_tokens", 1)
                * num_samples
                * output_token_cost,
            }
            for col in columns
        ],
    }
