import pytest
from clients.models import Client
from projects.models import Project
from invoices.models import Invoice
from django.utils import timezone

@pytest.fixture
def project(db):
    """Фикстура для создания проекта"""
    client = Client.objects.create(name="Fixture Client")
    return Project.objects.create(
        name="Fixture Project",
        client=client,
        budget=1000
    )

@pytest.fixture
def invoice(db, project):
    """Фикстура для создания инвойса (использует фикстуру project)"""
    return Invoice.objects.create(
        project=project,
        number="INV-2026-999",
        amount=500.00,
        due_date=timezone.now().date(),
        status='draft'
    )