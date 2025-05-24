import asyncio

from modelmint_back.mcp_tools.synthetic_data_generation_tools import (
    generate_synthetic_data,
)


async def main():
    results = await generate_synthetic_data(
        data_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
                "email": {"type": "string"},
            },
            "required": ["name", "age", "email"],
        },
        num_samples=10,
    )
    print(results)


asyncio.run(main())
