from modelmint_back import mcp
from modelmint_back.mcp_tools import *

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
    # print(list_gpu_instances("lambda_labs"))

    # print(generate_synthetic_data(
    #     data_schema={
    #         "type": "object",
    #         "properties": {
    #             "name": {"type": "string"},
    #             "age": {"type": "number"},
    #             "email": {"type": "string"},
    #         },
    #         "required": ["name", "age", "email"],
    #     },
    #     num_samples=10,
    # ))
