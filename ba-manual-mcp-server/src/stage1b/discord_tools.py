import os
from typing import Annotated, Optional

from mcp.types import ToolExecution, CallToolResult, TextContent
from pydantic import Field
from server import mcp

from src.discord_client.api.default_api import DefaultApi
from src.discord_client.api_client import ApiClient
from src.discord_client.configuration import Configuration
from src.discord_client.models import CreateThreadRequest, CreateForumThreadRequest, \
    CreateTextThreadWithoutMessageRequest
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output

bot_token = os.environ.get("DISCORD_BOT")
if not bot_token:
    raise ValueError("DISCORD_BOT environment variable is required but not set")

config = Configuration(
    host = "https://discord.com/api/v10",
    api_key={"BotToken": "Bot " + bot_token}
)
api_client = ApiClient(configuration=config)
api = DefaultApi(api_client=api_client)

snowflake_pattern = "^(0|[1-9][0-9]*)$"

@rate_limit()
@sanitize_output()
@mcp.tool()
async def list_my_guilds(before: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, after: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, limit: Annotated[Optional[int], Field(gt=0,le=200)] = None, with_counts: Optional[bool] = None):
    try:
        guilds = await api.list_my_guilds(before=before, after=after, limit=limit, with_counts=with_counts)
        return guilds
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def list_guild_channels(guild_id: Annotated[str, Field(pattern=snowflake_pattern)]):
    try:
        channels = await api.list_guild_channels(guild_id=guild_id)
        return channels
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@rate_limit()
@sanitize_output()
@mcp.tool()
async def list_messages(channel_id: Annotated[str, Field(pattern=snowflake_pattern)], around: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, before: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, after: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, limit: Annotated[Optional[int], Field(gt=0,le=100)] = None):
    try:
        messages = await api.list_messages(channel_id=channel_id, around=around, before=before, after=after, limit=limit)
        return messages
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def create_thread(channel_id: Annotated[str, Field(pattern=snowflake_pattern)], thread: CreateForumThreadRequest | CreateTextThreadWithoutMessageRequest):
    try:
        thread = await api.create_thread(channel_id=channel_id, create_thread_request={"actual_instance": thread})
        return thread
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def list_guild_invites(guild_id: Annotated[str, Field(pattern=snowflake_pattern)]):
    try:
        invites = await api.list_guild_invites(guild_id=guild_id)
        return invites
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)