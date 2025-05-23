from mcp.server.fastmcp import FastMCP


mcp = FastMCP("modelmint")

# Import GPU cloud tools to register them with MCP
from . import gpu_cloud_tools
