from datetime import date
from enum import Enum
from typing import Annotated, Optional

from mcp.types import CallToolResult, TextContent
from pydantic import Field

from server import mcp
from src.eve_client.api.universe_api import UniverseApi
from src.eve_client.api_client import ApiClient
from src.eve_client.configuration import Configuration
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output

config = Configuration(
    host = "https://esi.evetech.net"
)
api_client = ApiClient(configuration=config)
api = UniverseApi(api_client=api_client)

class CompatibilityDate(Enum):
    DATE_2025_11_06 = "2025-11-06"

class AcceptLanguage(Enum):
    EN = "en"
    DE = "de"
    FR = "fr"
    JA = "ja"
    RU = "ru"
    ZH = "zh"
    KO = "ko"
    ES = "es"


@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_universe_categories_category_id(category_id: Annotated[int, Field(description="An Eve item category ID")], x_compatibility_date: Annotated[CompatibilityDate, Field(description="The compatibility date for the request.", )], accept_language: Annotated[AcceptLanguage, Field(description="The language to use for the response.")] = AcceptLanguage.EN, if_none_match: Annotated[Optional[str], Field(description="The ETag of the previous request. A 304 will be returned if this matches the current ETag.")] = None, x_tenant: Annotated[str, Field(description="The tenant ID for the request.")] = "tranquility"):
    """Get information of an item category. This route expires daily at 11:05"""
    try:
        categories = await api.get_universe_categories_category_id(category_id=category_id, x_compatibility_date=x_compatibility_date.value, accept_language=accept_language.value, if_none_match=if_none_match, x_tenant=x_tenant)
        return categories
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_universe_groups_group_id(group_id: Annotated[int, Field(description="An Eve item group ID")], x_compatibility_date: Annotated[CompatibilityDate, Field(description="The compatibility date for the request.")], accept_language: Annotated[AcceptLanguage, Field(description="The language to use for the response.")] = AcceptLanguage.EN, if_none_match: Annotated[Optional[str], Field(description="The ETag of the previous request. A 304 will be returned if this matches the current ETag.")] = None, x_tenant: Annotated[str, Field(description="The tenant ID for the request.")] = "tranquility"):
    """Get information on an item group. This route expires daily at 11:05"""
    try:
        groups = await api.get_universe_groups_group_id(group_id=group_id, x_compatibility_date=x_compatibility_date.value, accept_language=accept_language.value, if_none_match=if_none_match, x_tenant=x_tenant)
        return groups
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def post_universe_ids(ids: Annotated[list[str], Field(description="")], x_compatibility_date: Annotated[CompatibilityDate, Field(description="The compatibility date for the request.")], accept_language: Annotated[AcceptLanguage, Field(description="The language to use for the response.")] = AcceptLanguage.EN, if_none_match: Annotated[Optional[str], Field(description="The ETag of the previous request. A 304 will be returned if this matches the current ETag.")] = None, x_tenant: Annotated[str, Field(description="The tenant ID for the request.")] = "tranquility"):
    """Resolve a set of names to IDs in the following categories: agents, alliances, characters, constellations, corporations factions, inventory_types, regions, stations, and systems. Only exact matches will be returned. All names searched for are cached for 12 hours"""
    try:
        names = await api.post_universe_ids(request_body=ids, x_compatibility_date=x_compatibility_date.value, accept_language=accept_language.value, if_none_match=if_none_match, x_tenant=x_tenant)
        return names
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_universe_types_type_id(type_id: Annotated[int, Field(description="An Eve item type ID")], x_compatibility_date: Annotated[CompatibilityDate, Field(description="The compatibility date for the request.")], accept_language: Annotated[AcceptLanguage, Field(description="The language to use for the response.")] = AcceptLanguage.EN, if_none_match: Annotated[Optional[str], Field(description="The ETag of the previous request. A 304 will be returned if this matches the current ETag.")] = None, x_tenant: Annotated[str, Field(description="The tenant ID for the request.")] = "tranquility"):
    """Get information on a type. This route expires daily at 11:05"""
    try:
        types = await api.get_universe_types_type_id(type_id=type_id, x_compatibility_date=x_compatibility_date.value, accept_language=accept_language.value, if_none_match=if_none_match, x_tenant=x_tenant)
        return types
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)
