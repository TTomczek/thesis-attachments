import os
from typing import Annotated, Optional, List

import jq
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
async def list_my_guilds(before: Annotated[
    Optional[str], Field(description="Only return guilds before guild with this id.",
                         pattern=snowflake_pattern)] = None, after: Annotated[
    Optional[str], Field(description="Only return guilds after guild with this id.", pattern=snowflake_pattern)] = None,
                         limit: Annotated[Optional[int], Field(description="Maximum numbers of guilds to return.", gt=0,
                                                               le=200)] = None, with_counts: Annotated[
            Optional[bool], Field(description="Include approximate member and presence counts in response.")] = None,
                         jq_filter: Annotated[Optional[str], Field(
                             description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """Lists all guilds, also known as servers; the current user is a member of."""
    try:
        guilds = await api.list_my_guilds(before=before, after=after, limit=limit, with_counts=with_counts)

        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([guild.model_dump(mode="json") for guild in guilds]).all()
        else:
            return guilds
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def list_guild_channels(
        guild_id: Annotated[str, Field(description="The id of the guild.", pattern=snowflake_pattern)],
                         jq_filter: Annotated[Optional[str], Field(
                             description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """Lists all channels in a guild."""
    try:
        channels = await api.list_guild_channels(guild_id=guild_id)

        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([channel.model_dump(mode="json") for channel in channels]).all()
        else:
            return channels
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def list_messages(
        channel_id: Annotated[str, Field(description="The id of the channel.", pattern=snowflake_pattern)],
        around: Annotated[Optional[str], Field(description="The id of the message to return messages around.",
                                               pattern=snowflake_pattern)] = None, before: Annotated[
            Optional[str], Field(description="The id of the message to return messages before.",
                                 pattern=snowflake_pattern)] = None, after: Annotated[
            Optional[str], Field(description="The id of the message to return messages after.",
                                 pattern=snowflake_pattern)] = None, limit: Annotated[
            Optional[int], Field(description="Maximum number of messages to return.", gt=0, le=100)] = None,
                         jq_filter: Annotated[Optional[str], Field(
                             description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """List messages in a channel from newest to oldest."""
    try:
        messages = await api.list_messages(channel_id=channel_id, around=around, before=before, after=after,
                                           limit=limit)
        
        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([message.model_dump(mode="json") for message in messages]).all()
        else:
            return messages
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def create_thread(
        channel_id: Annotated[str, Field(description="The id of the channel.", pattern=snowflake_pattern)],
        thread: Annotated[CreateForumThreadRequest | CreateTextThreadWithoutMessageRequest, Field(
            description="The thread to create.")],
                         jq_filter: Annotated[Optional[str], Field(
                             description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """Start a thread without a message."""
    try:
        thread = await api.create_thread(channel_id=channel_id, create_thread_request={"actual_instance": thread})

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[TextContent(type="text", text=jq.compile(jq_filter).input_value(thread.model_dump(mode="json")).all())], isError=False)
        else:
            return thread
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def list_guild_invites(
        guild_id: Annotated[str, Field(description="The id of the guild.", pattern=snowflake_pattern)],
                         jq_filter: Annotated[Optional[str], Field(
                             description="An optional jq filter to apply to the result, to customize the result format.")] = None):
    """Lists all active guild invites."""
    try:
        invites = await api.list_guild_invites(guild_id=guild_id)

        if jq_filter is not None and jq_filter != "":
            return jq.compile(jq_filter).input_value([invite.model_dump(mode="json") for invite in invites]).all()
        else:
            return invites
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)
