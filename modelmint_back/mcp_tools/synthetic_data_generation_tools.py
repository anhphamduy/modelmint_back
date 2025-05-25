import asyncio
import json
from typing import Any, Dict, List

from dependency_injector.wiring import Provide, inject

from modelmint_back import mcp
from modelmint_back.core.di import Container
from modelmint_back.core.settings import settings
from modelmint_back.models.synthetic_data_models import (RunStatus,
                                                         SyntheticData,
                                                         SyntheticDataRun)


@mcp.tool()
@inject
async def generate_synthetic_data(
    data_schema: Dict[str, Any],
    num_samples: int = 10,
    client=Provide[Container.synthetic_data_llm_client],
    db_session=Provide[Container.database_session],
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
