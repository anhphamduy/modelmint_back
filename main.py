from modelmint_back import mcp
from modelmint_back.mcp_tools import *

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
