from datetime import date

import jq
from enum import Enum
from typing import Annotated, Optional

from mcp.types import CallToolResult, TextContent
from pydantic import Field
from toon_format import encode

from src.eve_client.api.universe_api import UniverseApi
from src.eve_client.api_client import ApiClient
from src.eve_client.configuration import Configuration
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output
from server import mcp

config = Configuration(
    host="https://esi.evetech.net"
)
api_client = ApiClient(configuration=config)
api = UniverseApi(api_client=api_client)


class CompatibilityDate(Enum):
    DATE_2025_11_06 = "2025-11-06"

# Ruft alle Informationen zu einem Schiff anhand es Namens ab
# Enthält PostUniverseIds, GetUniverseTypesTypeId
@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_ship_infos(
        ship_name: Annotated[str, Field(description="The name of the ship.")],
        jq_filter: Annotated[Optional[str], Field(description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Get information about a ship by its name."""
    try:
        ids = await api.post_universe_ids(x_compatibility_date=date(2025,11,6), request_body=[ship_name])

        if not hasattr(ids, 'inventory_types') or ids.inventory_types is None:
            return CallToolResult(content=[TextContent(type="text", text=f"Ship '{ship_name}' not found.")], isError=False)

        types = []
        print(ids)
        for inventory_type in ids.inventory_types:
            types.extend(await api.get_universe_types_type_id(type_id=inventory_type.id, x_compatibility_date=date(2025,11,6)))

        if jq_filter is not None and jq_filter != "":
            return encode(jq.compile(jq_filter).input_value([type for type in types]).all())
        else:
            return encode([type for type in types])

    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

# Holt direkt alle Typen einer Kategorie
# Enthält GetUniverseCategoriesCategoryId, GetUniverseGroupsGroupId
@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_type_ids_of_category(
        category_name: Annotated[str, Field(description="Name of the category.")],
        jq_filter: Annotated[Optional[str], Field(description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Get all list of type ids of groups in a category. Returns a list of type IDs."""
    try:
        category_ids = await api.get_universe_categories(x_compatibility_date=date(2025,11,6))

        category = None
        category_name_lower = category_name.lower()
        for category_id in category_ids:
            temp_category = await api.get_universe_categories_category_id(category_id=category_id, x_compatibility_date=date(2025,11,6))
            if temp_category.name.lower() == category_name_lower:
                category = temp_category
                break

        if category is None:
            return CallToolResult(content=[TextContent(type="text", text=f"Category '{category_name}' not found.")], isError=False)

        category_answer = await api.get_universe_categories_category_id(category_id=category.category_id, x_compatibility_date=date(2025,11,6))
        type_ids = []
        for group_id in category_answer.groups:
            types_of_group = await api.get_universe_groups_group_id(group_id=group_id, x_compatibility_date=date(2025,11,6))
            type_ids.extend(types_of_group.types)

        if jq_filter is not None and jq_filter != "":
            return encode(jq.compile(jq_filter).input_value(type_ids).all())
        else:
            return encode(type_ids)
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


