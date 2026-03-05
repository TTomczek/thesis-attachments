from datetime import date
from enum import Enum
from typing import Annotated, Optional, List

import jq
from mcp.types import CallToolResult, TextContent
from pydantic import Field, BaseModel
from server import mcp
from toon_format import encode

from src.invman_client.api.business_partners_api import BusinessPartnersApi
from src.invman_client.api.contact_persons_api import ContactPersonsApi
from src.invman_client.api.files_api import FilesApi
from src.invman_client.api.invoice_positions_api import InvoicePositionsApi
from src.invman_client.api.invoice_templates_api import InvoiceTemplatesApi
from src.invman_client.api.invoices_api import InvoicesApi
from src.invman_client.api.sales_taxes_api import SalesTaxesApi
from src.invman_client.api_client import ApiClient
from src.invman_client.configuration import Configuration
from src.invman_client.models.sales_tax import SalesTax
from src.rate_limiter import rate_limit
from src.sanitize_output import sanitize_output

config = Configuration(
    host="http://localhost:8080/invoice-manager-server"
)
api_client = ApiClient(configuration=config)
business_partner_api = BusinessPartnersApi(api_client=api_client)
contact_person_api = ContactPersonsApi(api_client=api_client)
files_Api = FilesApi(api_client=api_client)
invoice_positions_api = InvoicePositionsApi(api_client=api_client)
invoice_template_api = InvoiceTemplatesApi(api_client=api_client)
invoices_api = InvoicesApi(api_client=api_client)
sales_taxes_api = SalesTaxesApi(api_client=api_client)


# Holt alle Rechnungen, mit Namen anstatt Ids
# Enthält getAllInvoices, getAllBusinessPartners
@mcp.tool()
@rate_limit()
@sanitize_output()
async def get_invoices(
        paid: Annotated[Optional[bool], Field(description="Filter invoices by paid status. Ignore for both.")] = None,
        customer_name: Annotated[Optional[str], Field(description="The name of the customer.")] = None,
        receiver_name: Annotated[
            Optional[str], Field(description="The name of the employee of a customer to send the invoice to.")] = None,
        order_number: Annotated[Optional[str], Field(description="Filter invoices by order number")] = None,
        jq_filter: Annotated[Optional[str], Field(
            description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Get all invoices matching the given filters."""
    try:
        customer_id = None
        receiver_id = None

        if customer_name is not None:
            customer_id = await find_customer_id_by_name(customer_name)

        if receiver_id is not None:
            receiver_id = await find_receiver_id_by_name(receiver_name)

        invoices = await invoices_api.get_all_invoices(paid=paid,
                                                       customer_number=customer_id,
                                                       receiver_id=receiver_id,
                                                       order_number=order_number)

        if jq_filter is not None and jq_filter != "":
            return encode(
                jq.compile(jq_filter).input_value([invoice.model_dump(mode="json") for invoice in invoices]).all)
        else:
            return encode([invoice.model_dump(mode="json") for invoice in invoices])
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


class Unit(Enum):
    """Represents the unit of an invoice position."""
    HOUR = "hour"
    PD = "pd"
    PIECE = "piece"


class InvoicePosition(BaseModel):
    """Represents a position of an invoice."""
    description: Annotated[Optional[str], Field(description="The description of the invoice position.")] = None
    price_per_unit_in_cents: Annotated[int, Field(description="The price per unit in cents.")]
    quantity: Annotated[int, Field(description="The quantity of the invoice position.")]
    unit: Annotated[Unit, Field(description="The unit of the invoice position.")]


class Invoice(BaseModel):
    """Represents an invoice."""
    description: Annotated[Optional[str], Field(description="The description of the invoice.")] = None
    via_mail: Annotated[Optional[bool], Field(description="Whether the invoice should be sent by mail.")] = True
    pre_text: Annotated[
        Optional[str], Field(description="The text that should be added to the beginning of the invoice.")] = None
    post_text: Annotated[
        Optional[str], Field(description="The text that should be added to the end of the invoice.")] = None
    service_from: Annotated[date, Field(description="The date from which the service is provided.")]
    service_to: Annotated[Optional[date], Field(description="The date until which the service is provided.")] = None
    order_number: Annotated[Optional[str], Field(description="The order number of the invoice.")] = None
    customer_name: Annotated[str, Field(description="The name of the customer.")]
    receiver_name: Annotated[Optional[str], Field(description="The name of the person to send the invoice to.")] = None
    positions: Annotated[
        Optional[List[InvoicePosition]], Field(description="The positions of the invoice.", min_length=1)] = None
    sales_tax: Annotated[float, Field(description="The rate of the applicable sales tax of the invoice.")]
    invoice_template: Annotated[str, Field(description="The name of the page template of the invoice.")]


# Erstellt neue Rechnung mit Namen und Positionen
# Enthält createInvoice, createPosition, getAllBusinessPartners, getAllSalesTaxes, getAllInvoiceTemplates
@mcp.tool()
@rate_limit()
@sanitize_output()
async def create_invoice(
        invoice: Annotated[Invoice, Field(description="The invoice to create.")],
        jq_filter: Annotated[Optional[str], Field(
            description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Create a new invoice"""
    try:
        customer_id = await find_customer_id_by_name(invoice.customer_name)
        receiver_id = None
        sales_tax_id = await find_sales_tax_id_by_value(invoice.sales_tax)
        invoice_template_id = await find_invoice_template_id_by_name(invoice.invoice_template)

        if invoice.receiver_name is not None:
            receiver_id = await find_receiver_id_by_name(invoice.receiver_name)

        invoice_dto = {
            "id": None,
            "description": invoice.description,
            "viaMail": invoice.via_mail,
            "preText": invoice.pre_text,
            "postText": invoice.post_text,
            "serviceFrom": invoice.service_from,
            "serviceTo": invoice.service_to,
            "orderNumber": invoice.order_number,
            "customerNumber": customer_id,
            "paid": False,
            "positions": [],
            "receiver": receiver_id,
            "salesTax": sales_tax_id,
            "invoiceTemplate": invoice_template_id,
            "file": None
        }

        created_invoice = await invoices_api.create_invoice(invoice_dto)

        created_position_ids = []
        for position in invoice.positions:
            position_dto = {
                "description": position.description,
                "pricePerUnitInCents": position.price_per_unit_in_cents,
                "quantity": position.quantity,
                "unit": position.unit.value,
                "invoice": created_invoice.id
            }
            created_positions = await invoice_positions_api.create_position(invoice_position=position_dto)
            created_position_ids.append(created_positions.id)

        created_invoice.positions = created_position_ids
        updated_invoice = await invoices_api.update_invoice_by_id(id=created_invoice.id, invoice=created_invoice)

        if jq_filter is not None and jq_filter != "":
            return encode(jq.compile(jq_filter).input_value(updated_invoice.model_dump(mode="json")).all())
        else:
            return encode(updated_invoice.model_dump(mode="json"))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


# Erstellt und läd eine Rechnung herunter
# Enthält getInvoicePdfById, downloadFileById
@mcp.tool()
@rate_limit()
@sanitize_output()
async def download_invoice(
        invoice_id: Annotated[int, Field(description="The id of the invoice to download.")],
        jq_filter: Annotated[Optional[str], Field(
            description="An optional jq filter to apply to the result, to customize the result format.")] = None
):
    """Create a downloadable file for an invoice and download it."""

    try:
        file_id = await invoices_api.get_invoice_pdf_by_id(invoice_id)
        file = await files_Api.download_file_by_id(file_id)

        if jq_filter is not None and jq_filter != "":
            return encode(jq.compile(jq_filter).input_value(file.model_dump(mode="json")).all())
        else:
            return encode(file.model_dump(mode="json"))
    except Exception as e:
        return CallToolResult(content=[TextContent(type="text", text=str(e))], isError=True)


async def find_customer_id_by_name(customer_name: str):
    business_partners = await business_partner_api.get_all_business_partners(name=customer_name)
    if len(business_partners) == 0:
        raise ValueError(f"Customer '{customer_name}' not found.")
    elif len(business_partners) > 1:
        raise ValueError(
            f"Multiple customers found with name '{customer_name}'. Found {",".join([bp.name for bp in business_partners])}")
    else:
        return business_partners[0].id


async def find_receiver_id_by_name(receiver_name: str):
    contact_persons = await contact_person_api.get_all_contact_persons(name=receiver_name)
    if len(contact_persons) == 0:
        raise ValueError(f"Receiver '{receiver_name}' not found.")
    elif len(contact_persons) > 1:
        raise ValueError(
            f"Multiple receivers found with name '{receiver_name}'. Known contact persons: {','.join([f'{contact.first_name} {contact.name}' for contact in contact_persons])}"
        )
    else:
        return contact_persons[0].id


async def find_sales_tax_id_by_value(sales_tax_value: float):
    sales_taxes: list[SalesTax] = await sales_taxes_api.get_all_sales_taxes()
    for sales_tax in sales_taxes:
        if sales_tax.rate == sales_tax_value:
            return sales_tax.id
    raise ValueError(f"Sales tax with rate '{sales_tax_value}' not found. Known sales taxes: {','.join([f'{tax.name}({tax.rate})' for tax in sales_taxes])}")


async def find_invoice_template_id_by_name(invoice_template_name: str):
    invoice_templates = await invoice_template_api.get_all_invoice_templates()
    invoice_template_name_lower = invoice_template_name.lower()
    for invoice_template in invoice_templates:
        if invoice_template.name.lower() == invoice_template_name_lower:
            return invoice_template.id
    raise ValueError(f"Invoice template '{invoice_template_name}' not found. Known templates {','.join([template.name for template in invoice_templates])}")
