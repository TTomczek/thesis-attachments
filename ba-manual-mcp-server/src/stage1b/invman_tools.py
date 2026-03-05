from datetime import date
from enum import Enum
from typing import Annotated, Optional

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
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output

config = Configuration(
    host = "http://localhost:8080/invoice-manager-server"
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
    viaMail: Optional[bool] = None
    preText: Optional[str] = None
    postText: Optional[str] = None
    serviceFrom: date
    serviceTo: Optional[date] = None
    orderNumber: Optional[str] = None
    customerNumber: int
    paid: Optional[bool] = None
    positions: Optional[list[int]] = None
    receiver: Optional[int] = None
    sales_tax: int
    invoice_template: int
    file: Optional[int] = None


@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_all_invoices(paid: Annotated[Optional[bool], Field(description="Filter invoices by paid status")] = None, customer_number: Annotated[Optional[int], Field(description="Filter invoices by customer number")] = None, receiver_id: Annotated[Optional[int], Field(description="Filter invoices by receiver")] = None, order_number: Annotated[Optional[str], Field(description="Filter invoices by order number")] = None):
    """Get a list of all invoices with optional filters for paid status, customer number, receiver id, and order number."""
    try:
        invoices = await invoices_api.get_all_invoices(paid=paid, customer_number=customer_number, receiver_id=receiver_id, order_number=order_number)
        return invoices
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def create_invoice(invoice: Invoice):
    """Create a new invoice based on the provided invoice data."""
    invoice_data = {
        "description": invoice.description,
        "viaMail": invoice.viaMail,
        "preText": invoice.preText,
        "postText": invoice.postText,
        "serviceFrom": invoice.serviceFrom,
        "serviceTo": invoice.serviceTo,
        "orderNumber": invoice.orderNumber,
        "customerNumber": invoice.customerNumber,
        "paid": invoice.paid,
        "positions": invoice.positions,
        "receiver": invoice.receiver,
        "salesTax": invoice.sales_tax,
        "invoiceTemplate": invoice.invoice_template,
        "file": invoice.file
    }
    try:
        created_invoice = await invoices_api.create_invoice(invoice_data)
        return created_invoice
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_all_sales_taxes():
    """Get a list of all sales taxes."""
    try:
        sales_taxes = await sales_taxes_api.get_all_sales_taxes()
        return sales_taxes
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_all_business_partners(name: Annotated[Optional[str], Field(description="Filter business partners by name")] = None):
    """Get a list of all business partners with optional filter by name."""
    try:
        business_partners = await business_partner_api.get_all_business_partners(name=name)
        return business_partners
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_all_invoice_templates():
    """Get a list of all invoice templates."""
    try:
        invoice_templates = await invoice_template_api.get_all_invoice_templates()
        return invoice_templates
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


class Unit(Enum):
    HOUR = "hour"
    PD= "pd"
    PIECE = "piece"


class InvoicePosition(BaseModel):
    id: Optional[int] = None
    description: Optional[str] = None
    pricePerUnitInCents: int
    quantity: float
    unit: Unit
    invoice: int


@rate_limit()
@sanitize_output()
@mcp.tool()
async def create_position(position: InvoicePosition):
    """Create a new invoice position based on the provided Invoice Position object."""
    position_data = {
        "description": position.description,
        "pricePerUnitInCents": position.pricePerUnitInCents,
        "quantity": position.quantity,
        "unit": position.unit.value,
        "invoice": position.invoice
    }
    try:
        created_position = await invoice_positions_api.create_position(position_data)
        return created_position
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def update_invoice_by_id(id: Annotated[int, Field(description="The id of the invoice")], invoice: Invoice):
    """Update the details of an existing invoice using its unique identifier."""
    try:
        updated_invoice = await invoices_api.update_invoice_by_id(id=id, invoice=invoice)
        return updated_invoice
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def get_invoice_pdf_by_id(id: Annotated[int, Field(description="The id of the invoice")]):
    """Generate a pdf file for the invoice with the given id and returns its unique identifier."""
    try:
        pdf = await invoices_api.get_invoice_pdf_by_id(id=id)
        return pdf
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)

@rate_limit()
@sanitize_output()
@mcp.tool()
async def download_file_by_id(id: Annotated[int, Field(description="The id of the file")]):
    """Download a file by its unique identifier."""
    try:
        file = await files_Api.download_file_by_id(id=id)
        return file
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


