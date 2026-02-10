import pytest
from django.utils import timezone
from datetime import timedelta, date
from invoices.models import Invoice
from projects.models import Project
from clients.models import Client

@pytest.mark.django_db
class TestInvoiceModel:
    """Tests for the Invoice database model functionality"""

    def test_invoice_creation(self) -> None:
        """Verify successful invoice creation and its string representation"""
        # 1. Set up related objects
        client: Client = Client.objects.create(name="Test Client")
        project: Project = Project.objects.create(name="Project Alpha", client=client)

        # Define future due date
        invoice_due_date: date = timezone.now().date() + timedelta(days=10)

        # 2. Create the invoice instance
        invoice: Invoice = Invoice.objects.create(
            project=project,
            number="INV-2026-001",
            amount=5000.00,
            due_date=invoice_due_date,
            status='draft'
        )

        # 3. Assertions for data integrity and __str__ method
        assert invoice.number == "INV-2026-001"
        assert str(invoice) == f"Счёт INV-2026-001 — Project Alpha"
        assert invoice.status == 'draft'