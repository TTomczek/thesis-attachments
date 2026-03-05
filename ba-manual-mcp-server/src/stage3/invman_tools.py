from datetime import date
from enum import Enum
from typing import Annotated, Optional, List

from src.invman_client.models.business_partner import BusinessPartner
from src.invman_client.models.download_file import DownloadFile
from src.invman_client.models.invoice import Invoice as InvManInvoice
from src.invman_client.models.invoice_position import InvoicePosition as InvManInvoicePosition

from mcp.types import CallToolResult, TextContent
from pydantic import Field, BaseModel
from server import mcp

from src.invman_client.api.business_partners_api import BusinessPartnersApi
from src.invman_client.api.files_api import FilesApi
from src.invman_client.api.invoice_positions_api import InvoicePositionsApi
from src.invman_client.api.invoice_templates_api import InvoiceTemplatesApi
from src.invman_client.api.invoices_api import InvoicesApi
from src.invman_client.api.sales_taxes_api import SalesTaxesApi
from src.invman_client.api_client import ApiClient
from src.invman_client.configuration import Configuration
from src.invman_client.models.invoice_template import InvoiceTemplate
from src.invman_client.models.sales_tax import SalesTax
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output
from src.stage3.json_logger import json_logger

config = Configuration(
    host="http://localhost:8080/invoice-manager-server"
)
api_client = ApiClient(configuration=config)
business_partner_api = BusinessPartnersApi(api_client=api_client)
files_Api = FilesApi(api_client=api_client)
invoice_positions_api = InvoicePositionsApi(api_client=api_client)
invoice_template_api = InvoiceTemplatesApi(api_client=api_client)
invoices_api = InvoicesApi(api_client=api_client)
sales_taxes_api = SalesTaxesApi(api_client=api_client)


class Invoice(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    via_mail: Optional[bool] = None
    pre_text: Optional[str] = None
    post_text: Optional[str] = None
    service_from: date
    service_to: Optional[date] = None
    order_number: Optional[str] = None
    customer_number: int
    paid: Optional[bool] = None
    positions: Optional[list[int]] = None
    receiver: Optional[int] = None
    sales_tax: int
    invoice_template: int
    file: Optional[int] = None


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def get_all_invoices(paid: Annotated[Optional[bool], Field(description="Filter invoices by paid status")] = None,
                           customer_number: Annotated[
                               Optional[int], Field(description="Filter invoices by customer number")] = None,
                           receiver_id: Annotated[
                               Optional[int], Field(description="Filter invoices by receiver")] = None,
                           order_number: Annotated[
                               Optional[str], Field(description="Filter invoices by order number")] = None) -> \
Annotated[CallToolResult, List[InvManInvoice]]:
    """Get a list of all invoices with optional filters for paid status, customer number, receiver id, and order number."""
    try:
        invoices = await invoices_api.get_all_invoices(paid=paid, customer_number=customer_number,
                                                       receiver_id=receiver_id, order_number=order_number)
        return CallToolResult(content=[], structuredContent={ "result": [invoice.model_dump(by_alias=True) for invoice in invoices] })
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def create_invoice(invoice: Invoice) -> Annotated[CallToolResult, InvManInvoice]:
    """Create a new invoice based on the provided invoice data."""
    invoice_data = {
        "description": invoice.description,
        "via_mail": invoice.via_mail,
        "pre_text": invoice.pre_text,
        "post_text": invoice.post_text,
        "service_from": invoice.service_from,
        "service_to": invoice.service_to,
        "order_number": invoice.order_number,
        "customer_number": invoice.customer_number,
        "paid": invoice.paid,
        "positions": invoice.positions,
        "receiver": invoice.receiver,
        "sales_tax": invoice.sales_tax,
        "invoice_template": invoice.invoice_template,
        "file": invoice.file
    }
    try:
        created_invoice = await invoices_api.create_invoice(invoice_data)
        return CallToolResult(content=[], structuredContent=created_invoice.model_dump(by_alias=True))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def get_all_sales_taxes() -> Annotated[CallToolResult, List[SalesTax]]:
    """Get a list of all sales taxes."""
    try:
        sales_taxes = await sales_taxes_api.get_all_sales_taxes()
        return CallToolResult(content=[], structuredContent={"result": [tax.model_dump(by_alias=True) for tax in sales_taxes]})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def get_all_business_partners(
        name: Annotated[Optional[str], Field(description="Filter business partners by name")] = None) -> Annotated[CallToolResult, List[BusinessPartner]]:
    """Get a list of all business partners with optional filter by name."""
    try:
        business_partners = await business_partner_api.get_all_business_partners(name=name)
        return CallToolResult(content=[], structuredContent={"result": [partner.model_dump(by_alias=True) for partner in business_partners]})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def get_all_invoice_templates() -> Annotated[CallToolResult, List[InvoiceTemplate]]:
    """Get a list of all invoice templates."""
    try:
        invoice_templates = await invoice_template_api.get_all_invoice_templates()
        return CallToolResult(content=[], structuredContent={"result": [template.model_dump(by_alias=True) for template in invoice_templates]})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


class Unit(Enum):
    HOUR = "hour"
    PD = "pd"
    PIECE = "piece"


class InvoicePosition(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    pricePerUnitInCents: int
    quantity: float
    unit: Unit
    invoice: int


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def create_position(position: InvoicePosition) -> Annotated[CallToolResult, InvManInvoicePosition]:
    """Create a new invoice position based on the provided Invoice Position object."""
    position_data = {
        "description": position.description,
        "price_per_unit_in_cents": position.pricePerUnitInCents,
        "quantity": position.quantity,
        "unit": position.unit.value,
        "invoice": position.invoice
    }
    try:
        created_position = await invoice_positions_api.create_position(position_data)
        return CallToolResult(content=[], structuredContent=created_position.model_dump(by_alias=True))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def update_invoice_by_id(id: Annotated[int, Field(description="The id of the invoice")], invoice: Invoice) -> Annotated[CallToolResult, InvManInvoice]:
    """Update the details of an existing invoice using its unique identifier."""
    invoice_data = {
        "description": invoice.description,
        "via_mail": invoice.via_mail,
        "pre_text": invoice.pre_text,
        "post_text": invoice.post_text,
        "service_from": invoice.service_from,
        "service_to": invoice.service_to,
        "order_number": invoice.order_number,
        "customer_number": invoice.customer_number,
        "paid": invoice.paid,
        "positions": invoice.positions,
        "receiver": invoice.receiver,
        "sales_tax": invoice.sales_tax,
        "invoice_template": invoice.invoice_template,
        "file": invoice.file
    }
    try:
        updated_invoice: InvManInvoice = await invoices_api.update_invoice_by_id(id=id, invoice=invoice_data)
        return CallToolResult(content=[], structuredContent=updated_invoice.model_dump(by_alias=True))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def get_invoice_pdf_by_id(id: Annotated[int, Field(description="The id of the invoice")]) -> Annotated[CallToolResult, int]:
    """Generate a pdf file for the invoice with the given id and returns its unique identifier."""
    try:
        pdf = await invoices_api.get_invoice_pdf_by_id(id=id)
        return CallToolResult(content=[], structuredContent={"result": pdf})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
@json_logger()
async def download_file_by_id(id: Annotated[int, Field(description="The id of the file")]) -> Annotated[CallToolResult, DownloadFile]:
    """Download a file by its unique identifier."""
    try:
        file = await files_Api.download_file_by_id(id=id)
        return CallToolResult(content=[], structuredContent={"result": file.model_dump(by_alias=True)})
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)
