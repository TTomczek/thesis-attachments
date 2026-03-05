import os
from typing import Annotated, Optional, List

from mcp.types import CallToolResult, TextContent
from pydantic import Field
from server import mcp

from src.discord_client.api.default_api import DefaultApi
from src.discord_client.api_client import ApiClient
from src.discord_client.configuration import Configuration
from src.discord_client.models import CreateForumThreadRequest, \
    CreateTextThreadWithoutMessageRequest, MyGuildResponse, GetChannel200Response, MessageResponse, \
    CreatedThreadResponse, ListChannelInvites200ResponseInner
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output
from src.stage3.json_logger import json_logger

bot_token = os.environ.get("DISCORD_BOT")
if not bot_token:
    raise ValueError("DISCORD_BOT environment variable is required but not set")

config = Configuration(
    host="https://discord.com/api/v10",
    api_key={"BotToken": "Bot " + bot_token}
)
api_client = ApiClient(configuration=config)
api = DefaultApi(api_client=api_client)

snowflake_pattern = "^(0|[1-9][0-9]*)$"


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def list_my_guilds(before: Annotated[
    Optional[str], Field(description="Only return guilds before guild with this id.",
                         pattern=snowflake_pattern)] = None, after: Annotated[
    Optional[str], Field(description="Only return guilds after guild with this id.", pattern=snowflake_pattern)] = None,
                         limit: Annotated[Optional[int], Field(description="Maximum numbers of guilds to return.", gt=0,
                                                               le=200)] = None, with_counts: Annotated[
            Optional[bool], Field(description="Include approximate member and presence counts in response.")] = None) -> \
Annotated[CallToolResult, List[MyGuildResponse]]:
    """Lists all guilds, also known as servers; the current user is a member of."""
    try:
        guilds = await api.list_my_guilds(before=before, after=after, limit=limit, with_counts=with_counts)
        return CallToolResult(content=[], structuredContent={"result": [guild.model_dump() for guild in guilds]})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def list_guild_channels(
        guild_id: Annotated[str, Field(description="The id of the guild.", pattern=snowflake_pattern)]) -> Annotated[
    CallToolResult, List[GetChannel200Response]]:
    """Lists all channels in a guild."""
    try:
        channels = await api.list_guild_channels(guild_id=guild_id)
        return CallToolResult(content=[], structuredContent={"result": [channel.model_dump() for channel in channels]})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def list_messages(
        channel_id: Annotated[str, Field(description="The id of the channel.", pattern=snowflake_pattern)],
        around: Annotated[Optional[str], Field(description="The id of the message to return messages around.",
                                               pattern=snowflake_pattern)] = None, before: Annotated[
            Optional[str], Field(description="The id of the message to return messages before.",
                                 pattern=snowflake_pattern)] = None, after: Annotated[
            Optional[str], Field(description="The id of the message to return messages after.",
                                 pattern=snowflake_pattern)] = None, limit: Annotated[
            Optional[int], Field(description="Maximum number of messages to return.", gt=0, le=100)] = None) -> \
Annotated[CallToolResult, List[MessageResponse]]:
    """List messages in a channel from newest to oldest."""
    try:
        messages = await api.list_messages(channel_id=channel_id, around=around, before=before, after=after,
                                           limit=limit)
        return CallToolResult(content=[], structuredContent={"result": [message.model_dump() for message in messages]})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def create_thread(
        channel_id: Annotated[str, Field(description="The id of the channel.", pattern=snowflake_pattern)],
        thread: Annotated[CreateForumThreadRequest | CreateTextThreadWithoutMessageRequest, Field(
            description="The thread to create.")]) -> Annotated[CallToolResult, CreatedThreadResponse]:
    """Start a thread without a message."""
    try:
        thread = await api.create_thread(channel_id=channel_id, create_thread_request={"actual_instance": thread})
        return CallToolResult(content=[], structuredContent={"result": thread.model_dump()})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def list_guild_invites(
        guild_id: Annotated[str, Field(description="The id of the guild.", pattern=snowflake_pattern)]) -> Annotated[CallToolResult, List[ListChannelInvites200ResponseInner]]:
    """Lists all active guild invites."""
    try:
        invites = await api.list_guild_invites(guild_id=guild_id)
        return CallToolResult(content=[], structuredContent={"result": [invite.model_dump() for invite in invites]})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)
