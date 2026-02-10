import pytest
from django.urls import reverse
from clients.models import Client


@pytest.mark.django_db
class TestClientViews:

    def test_client_list_view(self, client):
        """Checking the client list and pagination"""
        # Create 9 clients (the paginator has a limit of 8)
        for i in range(9):
            Client.objects.create(name=f"Client {i}")

        url = reverse('clients:list')  # Убедись, что namespace совпадает с urls.py
        response = client.get(url)

        assert response.status_code == 200
        # We check that there are 8 clients on the first page
        assert len(response.context['clients']) == 8

    def test_client_detail_view(self, client):
        """Checking the Customer Details Page"""
        c = Client.objects.create(name="Target Client")
        url = reverse('clients:detail', kwargs={'pk': c.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['client'].name == "Target Client"