from server import mcp

# Set import to wanted stage, to use the mcp server

import stage6.github_tools
# import stage6.discord_tools
# import stage6.eve_tools
# import stage6.invman_tools

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
