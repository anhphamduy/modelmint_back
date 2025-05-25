from mcp.server.fastmcp import FastMCP

from modelmint_back.core import Container, initialize_server

container = Container()
container.init_resources()

initialize_server()

mcp = FastMCP("modelmint")

container.wire(packages=["modelmint_back.mcp_tools"])

from .mcp_tools import *
