import pytest
from typing import List, Final
from datetime import timedelta
from django.utils import timezone
from clients.models import Client


@pytest.mark.django_db
class TestClientModel:
    """Tests for the Client database model"""

    def test_client_str(self) -> None:
        """Verify the string representation of the model instance"""
        client: Client = Client.objects.create(name="ООО Ромашка")
        assert str(client) == "ООО Ромашка"

    def test_formatted_phone_11_digits(self) -> None:
        """Verify phone formatting logic for standard 11-digit numbers"""
        client: Client = Client.objects.create(name="Иван", phone="89005553535")
        # Expected format: +7 900 555 3535
        assert client.formatted_phone == "+7 900 555 3535"

    def test_formatted_phone_short_number(self) -> None:
        """Verify that short numbers are returned without formatting"""
        client: Client = Client.objects.create(name="Иван", phone="123")
        assert client.formatted_phone == "123"

    def test_formatted_phone_none(self) -> None:
        """Verify that a placeholder is returned when the phone is empty"""
        client: Client = Client.objects.create(name="Иван", phone="")
        assert client.formatted_phone == "—"

    def test_ordering(self) -> None:
        """Verify that clients are ordered by creation date descending"""
        now: Final = timezone.now()

        # Create the first client and manually adjust the timestamp
        c1: Client = Client.objects.create(name="Первый")
        c1.created_at = now - timedelta(days=1)
        c1.save()

        # Create a newer client
        c2: Client = Client.objects.create(name="Второй")

        clients: List[Client] = list(Client.objects.all())

        # Ensure c2 appears before c1 in the result set
        assert clients[0] == c2
        assert clients[1] == c1

    def test_telegram_chat_id_optional(self) -> None:
        """Verify that the telegram_chat_id field allows null or blank values"""
        client: Client = Client.objects.create(name="Клиент без ТГ")
        assert client.telegram_chat_id in [None, ""]