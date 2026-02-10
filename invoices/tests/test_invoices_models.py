import pytest
from django.utils import timezone
from datetime import timedelta
from invoices.models import Invoice
from projects.models import Project
from clients.models import Client


@pytest.mark.django_db
class TestInvoiceModel:

    def test_invoice_creation(self):
        """Checking invoice creation and string representation"""
        client = Client.objects.create(name="Test Client")
        project = Project.objects.create(name="Project Alpha", client=client)

        invoice = Invoice.objects.create(
            project=project,
            number="INV-2026-001",
            amount=5000.00,
            due_date=timezone.now().date() + timedelta(days=10),
            status='draft'
        )

        assert invoice.number == "INV-2026-001"
        assert str(invoice) == f"Счёт INV-2026-001 — Project Alpha"
        assert invoice.status == 'draft'