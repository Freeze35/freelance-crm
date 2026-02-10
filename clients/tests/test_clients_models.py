import pytest
from clients.models import Client
from datetime import timedelta
from django.utils import timezone

@pytest.mark.django_db
class TestClientModel:
    """Testing the Client Model"""

    def test_client_str(self):
        """Checking the string representation of the model (__str__)"""
        client = Client.objects.create(name="ООО Ромашка")
        assert str(client) == "ООО Ромашка"

    def test_formatted_phone_11_digits(self):
        """Checking phone formatting when entering 11 digits"""
        client = Client.objects.create(name="Иван", phone="89005553535")
        # We are waiting: +7 900 555 3535
        assert client.formatted_phone == "+7 900 555 3535"

    def test_formatted_phone_short_number(self):
        """Check that the short code is returned as is (without formatting)"""
        client = Client.objects.create(name="Иван", phone="123")
        assert client.formatted_phone == "123"

    def test_formatted_phone_none(self):
        """Check that if the phone number is not specified, a dash is returned"""
        client = Client.objects.create(name="Иван", phone="")
        assert client.formatted_phone == "—"

    def test_ordering(self):
        """Ensure that new clients are listed first (sorting)"""
        # Let's create the first client a little earlier
        c1 = Client.objects.create(name="Первый")
        c1.created_at = timezone.now() - timedelta(days=1)
        c1.save()

        # We are creating a second client now.
        c2 = Client.objects.create(name="Второй")

        clients = Client.objects.all()

        # Now c2 is guaranteed to be newer than c1
        assert clients[0] == c2
        assert clients[1] == c1

    def test_telegram_chat_id_optional(self):
        """Checking if the telegram_chat_id field can be empty"""
        client = Client.objects.create(name="Клиент без ТГ")
        assert client.telegram_chat_id is None or client.telegram_chat_id == ""
