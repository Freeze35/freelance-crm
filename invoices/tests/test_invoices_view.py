import pytest
from django.urls import reverse
from unittest.mock import patch
from invoices.models import Invoice


@pytest.mark.django_db
class TestInvoiceViews:

    @patch('invoices.views.send_invoice_to_telegram.delay')
    def test_send_telegram_json_response(self, mock_delay, client, invoice):
        """We check that pressing the send button in TG returns success and triggers the task"""
        # We configure the project so that the client has a chat_id
        invoice.project.client.telegram_chat_id = '12345678'
        invoice.project.client.save()

        url = reverse('invoices:send_telegram', kwargs={'pk': invoice.id})
        response = client.post(url)

        assert response.status_code == 200
        assert response.json()['status'] == 'success'
        # Check that the Celery task was called
        mock_delay.assert_called_once_with(invoice.pk, '12345678')