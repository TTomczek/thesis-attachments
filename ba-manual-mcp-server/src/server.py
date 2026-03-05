import logging

from mcp.server import FastMCP

app_logger = logging.getLogger(__name__)
app_logger.setLevel(logging.DEBUG)
app_logger.addHandler(logging.FileHandler('mcp.log'))

mcp = FastMCP(port=3000)