import os
from typing import Annotated, Optional

from pydantic import Field

from server import mcp
from src.discord_client.models import CreateThreadRequest, CreateForumThreadRequest, \
    CreateTextThreadWithoutMessageRequest
from src.discord_client.api.default_api import DefaultApi
from src.discord_client.api_client import ApiClient
from src.discord_client.configuration import Configuration

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

@mcp.tool()
async def list_my_guilds(before: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, after: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, limit: Annotated[Optional[int], Field(gt=0,le=200)] = None, with_counts: Optional[bool] = None):
    guilds = await api.list_my_guilds(before=before, after=after, limit=limit, with_counts=with_counts)
    return guilds

@mcp.tool()
async def list_guild_channels(guild_id: Annotated[str, Field(pattern=snowflake_pattern)]):
    channels = await api.list_guild_channels(guild_id=guild_id)
    return channels

@mcp.tool()
async def list_messages(channel_id: Annotated[str, Field(pattern=snowflake_pattern)], around: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, before: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, after: Annotated[Optional[str], Field(pattern=snowflake_pattern)] = None, limit: Annotated[Optional[int], Field(gt=0,le=100)] = None):
    messages = await api.list_messages(channel_id=channel_id, around=around, before=before, after=after, limit=limit)
    return messages


# class ThreadAutoArchiveDuration(Enum):
#     ONE_HOUR = 60
#     ONE_DAY = 1440
#     THREE_DAY = 4320
#     SEVEN_DAY = 10080
#
#
# class BaseCreateMessageCreateRequest(BaseModel):
#     content: Annotated[str, Field(max_length=4000)] = None
#     embeds: Annotated[list[RichEmbed], Field(max_length=10)] = None
#     allowed_mentions: MessageAllowedMentionsRequest = None
#     sticker_ids: Annotated[list[str], Field(max_length=3)] = None
#     components: Annotated[list[str] | None, Field(max_length=40)] = None
#     flags: int | None = None
#     attachments: Annotated[list[MessageAttachmentRequest], Field(max_length=10)] = None
#     poll: PollCreateRequest = None
#     shared_client_theme: CustomClientThemeShareRequest = None
#     confetti_potion: Dict[str, Any] = None
#
#
# class CreateForumThreadRequest(BaseModel):
#     name: Annotated[str, Field(min_length=1, max_length=100)]
#     auto_archive_duration: ThreadAutoArchiveDuration | None = None
#     rate_limit_per_user: Annotated[int | None, Field(gt=0, le=21600)] = None
#     applied_tags: Annotated[list[str] | None, Field(max_length=5, pattern=snowflake_pattern)] = None
#     message: BaseCreateMessageCreateRequest
#
#
# class ChannelTypes(Enum):
#     ANNOUNCEMENT_THREAD = 10
#     PUBLIC_THREAD = 11
#     PRIVATE_THREAD = 12
#
#
# class CreateTextThreadWithoutMessageRequest(BaseModel):
#     name: Annotated[str, Field(min_length=1, max_length=100)]
#     auto_archive_duration: ThreadAutoArchiveDuration | None = None
#     rate_limit_per_user: Annotated[int | None, Field(gt=0, le=21600)] = None
#     applied_tags: Annotated[list[str] | None, Field(max_length=5, pattern=snowflake_pattern)] = None
#     type: ChannelTypes
#     invitable: bool | None = None


@mcp.tool()
async def create_thread(channel_id: Annotated[str, Field(pattern=snowflake_pattern)], thread: CreateForumThreadRequest | CreateTextThreadWithoutMessageRequest):
    thread = await api.create_thread(channel_id=channel_id, create_thread_request={"actual_instance": thread})
    return thread

@mcp.tool()
async def list_guild_invites(guild_id: Annotated[str, Field(pattern=snowflake_pattern)]):
    invites = await api.list_guild_invites(guild_id=guild_id)
    return invites