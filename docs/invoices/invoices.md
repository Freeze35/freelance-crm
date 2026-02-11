# Client Form Testing

This section documents the settings,view,forms,urls and models inside clients

## Invoice Model
The `Invoice` model is linked to a `Project`. It serves as the source of truth for billing and is used to generate PDF documents.

### Status Workflow
An invoice typically follows this lifecycle:
1. **Draft**: Initial creation, not yet visible to the client.
2. **Sent**: Dispatched via Telegram or Email.
3. **Paid / Partially Paid**: Payment received.
4. **Overdue**: System-marked status if the `due_date` has passed without full payment.

## Forms
::: invoices.forms
    options:
          show_root_heading: true
          show_source: true
          members_order: source

## Views
::: invoices.views
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Models
::: invoices.models
    options:
      show_root_heading: true
      show_source: true
      members_order: source

## Endpoint Overview

| URL Pattern | Name | View Function | Description |
| :--- | :--- | :--- | :--- |
| `projects/<int:project_id>/invoice/create/` | `create_from_project` | `invoice_create_from_project` | Generates a new invoice based on project details |
| `<int:invoice_id>/pdf/` | `pdf` | `generate_invoice_pdf` | Generates and downloads a PDF version of the invoice |
| `<int:pk>/update/` | `update` | `invoice_update` | Edit existing invoice data (amounts, dates, etc.) |
| `<int:pk>/delete/` | `delete` | `invoice_delete` | Permanently remove an invoice record |
| `<int:pk>/send-telegram/` | `send_telegram` | `send_invoice_telegram` | Manually trigger sending the invoice to the client's Telegram |