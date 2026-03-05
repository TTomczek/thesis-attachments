import os
from typing import Annotated, Optional

import jq
from mcp.types import CallToolResult, TextContent
from pydantic import Field
from toon_format import encode

from src.discord_client.api.default_api import DefaultApi
from src.discord_client.api_client import ApiClient
from src.discord_client.configuration import Configuration
from src.discord_client.models import MyGuildResponse, CreateForumThreadRequest, BaseCreateMessageCreateRequest
from server import mcp

from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output

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

# Holt alle Nachrichten eines Channels eines Servers
# Enthält listMyGuilds, listGuildChannels, listMessages
@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_messages_of_channel(
        server_name: Annotated[str, Field(description="The name of the server. Servers are also known as guilds.")],
        channel_name: Annotated[str, Field(description="The name of the channel.")],
        jq_filter: Annotated[Optional[str], Field(description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Get all messages of a channel in a server."""
    try:
        guild = await find_server_by_name(server_name)
    except ValueError as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    try:
        channel = await find_channel_by_name(guild, channel_name)
    except ValueError as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    try:
        messages = await api.list_messages(channel_id=channel.id)

        if jq_filter is not None and jq_filter != "":
            return encode(jq.compile(jq_filter).input_value([message.model_dump(mode="json") for message in messages]).all())
        else:
            return encode([message.model_dump(mode="json") for message in messages])
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


# Erstellt einen Thread in einem Channel
# Enthält listMyGuilds, listGuildChannels, createThread
@mcp.tool()
@rate_limit()
@sanitize_output()
async def create_thread_in_channel(
        server_name: Annotated[str, Field(description="The name of the server. Servers are also known as guilds.")],
        channel_name: Annotated[str, Field(description="The name of the channel.")],
        thread_title: Annotated[str, Field(description="The title of the thread.")],
        initial_message: Annotated[Optional[str], Field(description="The initial message of the thread.")] = None,
        jq_filter: Annotated[Optional[str], Field(description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Create a thread in a channel with an optional initial message."""
    try:
        guild = await find_server_by_name(server_name)
    except ValueError as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    try:
        channel = await find_channel_by_name(guild, channel_name)
    except ValueError as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    thread = await api.create_thread(channel_id=channel.id, create_thread_request={"actual_instance": CreateForumThreadRequest(name=thread_title, message=BaseCreateMessageCreateRequest(content=initial_message))})

    if jq_filter is not None and jq_filter != "":
        return encode(jq.compile(jq_filter).input_value(thread.model_dump(mode="json")).all())
    else:
        return encode(thread.model_dump(mode="json"))


# Holt alle Einladungen eines Servers
# Enthält listMyGuilds, listGuildInvites
@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_invites_of_server(
        server_name: Annotated[str, Field(description="The name of the server. Servers are also known as guilds.")],
        jq_filter: Annotated[Optional[str], Field(description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Get all invites of a server."""
    try:
        guild = await find_server_by_name(server_name)
    except ValueError as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

    invites = await api.list_guild_invites(guild_id=guild.id)

    if jq_filter is not None and jq_filter != "":
        return encode(jq.compile(jq_filter).input_value([invite.actual_instance.model_dump(mode="json") for invite in invites]).all())
    else:
        return encode([invite.actual_instance.model_dump(mode="json") for invite in invites])



async def find_server_by_name(server_name: str):
    guilds = await api.list_my_guilds()
    server_name_lower = server_name.lower()
    for guild in guilds:
        if guild.name.lower() == server_name_lower:
            return guild
    raise ValueError(f"Server with name '{server_name}' not found")

async def find_channel_by_name(guild: MyGuildResponse, channel_name: str):
    channels = await api.list_guild_channels(guild_id=guild.id)
    channel_name_lower = channel_name.lower()
    for channel in channels:
        if channel.actual_instance.name.lower() == channel_name_lower:
            return channel.actual_instance
    raise ValueError(f"Channel with name '{channel_name}' not found in server '{guild.name}'")