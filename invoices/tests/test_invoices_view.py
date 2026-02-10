import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import Client as DjangoTestClient
from typing import Any, Final

from invoices.models import Invoice


@pytest.mark.django_db
class TestInvoiceViews:
    """Tests for invoice views, focusing on external integrations like Telegram"""

    @patch('invoices.views.send_invoice_to_telegram.delay')
    def test_send_telegram_json_response(
            self,
            mock_delay: MagicMock,
            client: DjangoTestClient,
            invoice: Invoice
    ) -> None:
        """Verify that sending an invoice to TG returns success and triggers the Celery task"""

        # 1. Setup client's Telegram chat ID
        chat_id: Final[str] = '12345678'
        invoice.project.client.telegram_chat_id = chat_id
        invoice.project.client.save()

        # 2. Execute POST request to the send_telegram endpoint
        url: str = reverse('invoices:send_telegram', kwargs={'pk': invoice.pk})
        response: Any = client.post(url)

        # 3. Validation of the JSON response
        assert response.status_code == 200
        assert response.json().get('status') == 'success'

        # 4. Verify that the Celery task was triggered with correct arguments
        mock_delay.assert_called_once_with(invoice.pk, chat_id)