from datetime import date
from enum import Enum
from typing import Annotated, Optional, Any, Union, List

import jq
from mcp.types import CallToolResult, TextContent
from pydantic import Field, BaseModel
from server import mcp
from toon_format import encode

from src.invman_client.api.business_partners_api import BusinessPartnersApi
from src.invman_client.api.files_api import FilesApi
from src.invman_client.api.invoice_positions_api import InvoicePositionsApi
from src.invman_client.api.invoice_templates_api import InvoiceTemplatesApi
from src.invman_client.api.invoices_api import InvoicesApi
from src.invman_client.api.sales_taxes_api import SalesTaxesApi
from src.invman_client.api_client import ApiClient
from src.invman_client.configuration import Configuration
from src.invman_client.models.business_partner import BusinessPartner
from src.invman_client.models.download_file import DownloadFile
from src.invman_client.models.invoice import Invoice as InvManInvoice
from src.invman_client.models.invoice_position import InvoicePosition as InvManInvoicePosition
from src.invman_client.models.invoice_template import InvoiceTemplate
from src.invman_client.models.sales_tax import SalesTax
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output

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
async def get_all_invoices(paid: Annotated[Optional[bool], Field(description="Filter invoices by paid status")] = None,
                           customer_number: Annotated[
                               Optional[int], Field(description="Filter invoices by customer number")] = None,
                           receiver_id: Annotated[
                               Optional[int], Field(description="Filter invoices by receiver")] = None,
                           order_number: Annotated[
                               Optional[str], Field(description="Filter invoices by order number")] = None,
                           jq_filter: Annotated[Optional[str], Field(
                               description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> \
        Union[List[InvManInvoice], Any]:
    """Get a list of all invoices with optional filters for paid status, customer number, receiver id, and order number."""
    try:
        invoices = await invoices_api.get_all_invoices(paid=paid, customer_number=customer_number,
                                                       receiver_id=receiver_id, order_number=order_number)

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(jq.compile(jq_filter).input_(
                    [invoice.model_dump(mode="json") for invoice in invoices]).all())})
        else:
            return encode([invoice.model_dump(mode="json") for invoice in invoices])
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def create_invoice(invoice: Invoice,
                         jq_filter: Annotated[Optional[str], Field(
                             description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> \
        Union[InvManInvoice, Any]:
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

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(jq.compile(jq_filter).input_value(created_invoice.model_dump(mode="json")).all())})
        else:
            return encode(created_invoice.model_dump(mode="json"))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_all_sales_taxes(jq_filter: Annotated[Optional[str], Field(
    description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> Union[
    List[SalesTax], Any]:
    """Get a list of all sales taxes."""
    try:
        sales_taxes = await sales_taxes_api.get_all_sales_taxes()

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(
                    jq.compile(jq_filter).input_([tax.model_dump(mode="json") for tax in sales_taxes]).all())})
        else:
            return encode([sales_tax.model_dump(mode="json") for sales_tax in sales_taxes])
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_all_business_partners(
        name: Annotated[Optional[str], Field(description="Filter business partners by name")] = None,
        jq_filter: Annotated[Optional[str], Field(
            description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> \
        Union[List[BusinessPartner], Any]:
    """Get a list of all business partners with optional filter by name."""
    try:
        business_partners = await business_partner_api.get_all_business_partners(name=name)

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(jq.compile(jq_filter).input_(
                    [partner.model_dump(mode="json") for partner in business_partners]).all())})
        else:
            return encode([partner.model_dump(mode="json") for partner in business_partners])
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_all_invoice_templates(jq_filter: Annotated[Optional[str], Field(
    description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> Union[
    List[InvoiceTemplate], Any]:
    """Get a list of all invoice templates."""
    try:
        invoice_templates = await invoice_template_api.get_all_invoice_templates()

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(jq.compile(jq_filter).input_value(
                    [template.model_dump(mode="json") for template in invoice_templates]).all())})
        else:
            return encode([template.model_dump(mode="json") for template in invoice_templates])
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
async def create_position(position: InvoicePosition,
                          jq_filter: Annotated[Optional[str], Field(
                              description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> \
        Union[InvManInvoicePosition, Any]:
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

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(jq.compile(jq_filter).input_value(created_position.model_dump(mode="json")).all())})
        else:
            return encode(created_position.model_dump(mode="json"))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def update_invoice_by_id(id: Annotated[int, Field(description="The id of the invoice")], invoice: Invoice,
                               jq_filter: Annotated[Optional[str], Field(
                                   description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> \
        Union[InvManInvoice, Any]:
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

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(jq.compile(jq_filter).input_value(updated_invoice.model_dump(mode="json")).all())})
        else:
            return encode(updated_invoice.model_dump(mode="json"))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_invoice_pdf_by_id(id: Annotated[int, Field(description="The id of the invoice")]) -> int:
    """Generate a pdf file for the invoice with the given id and returns its unique identifier."""
    try:
        pdf = await invoices_api.get_invoice_pdf_by_id(id=id)

        return pdf
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


@mcp.tool()
@rate_limit()
@sanitize_output()
async def download_file_by_id(id: Annotated[int, Field(description="The id of the file")],
                              jq_filter: Annotated[Optional[str], Field(
                                  description="An optional jq filter to apply to the result, to customize the result format.")] = None) -> \
        Union[DownloadFile, Any]:
    """Download a file by its unique identifier."""
    try:
        file = await files_Api.download_file_by_id(id=id)

        if jq_filter is not None and jq_filter != "":
            return CallToolResult(content=[], structuredContent={
                "result": encode(jq.compile(jq_filter).input_value(file.model_dump(mode="json")).all())})
        else:
            return encode(file.model_dump(mode="json"))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)
