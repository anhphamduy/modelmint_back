import asyncio
from typing import Dict, List

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools


async def main() -> None:
    # Get all tools from mcp-server
    fetch_mcp_server = StdioServerParams(command="uv", args=["run", "main.py"])
    all_tools = await mcp_server_tools(fetch_mcp_server)
    
    # Categorize tools
    tool_categories: Dict[str, List] = {
        "synthetic_data": [],  # Tools for generating synthetic data
        "huggingface": [],     # Tools for interacting with Hugging Face models
        "gpu_cloud": [],       # Tools for managing GPU cloud instances
    }
    
    # Categorize each tool based on its name
    for tool in all_tools:
        if "synthetic_data" in tool.name:
            tool_categories["synthetic_data"].append(tool)
        elif "huggingface" in tool.name:
            tool_categories["huggingface"].append(tool)
        elif "gpu" in tool.name:
            tool_categories["gpu_cloud"].append(tool)
    
    # Print available tools in each category
    for category, tools in tool_categories.items():
        print(f"\n{category.upper()} Tools:")
        for tool in tools:
            print(f"- {tool.name}")

    # Example of how to use tools from a specific category
    # synthetic_data_tools = tool_categories["synthetic_data"]
    # huggingface_tools = tool_categories["huggingface"]
    # gpu_cloud_tools = tool_categories["gpu_cloud"]

    # # Create an agent with specific category of tools
    # model_client = OpenAIChatCompletionClient(model="gpt-4")
    # agent = AssistantAgent(
    #     name="tool_user",
    #     model_client=model_client,
    #     tools=synthetic_data_tools,  # or any other category
    #     reflect_on_tool_use=True
    # )


asyncio.run(main())
