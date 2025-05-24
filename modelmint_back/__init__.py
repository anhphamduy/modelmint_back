from mcp.server.fastmcp import FastMCP

from .di import Container

container = Container()
container.init_resources()


mcp = FastMCP("modelmint")

container.wire(packages=["modelmint_back.mcp_tools"])

from .mcp_tools import *
