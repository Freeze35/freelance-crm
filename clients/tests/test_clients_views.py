import pytest
from django.urls import reverse
from django.test import Client as DjangoTestClient
from django.template.response import TemplateResponse
from clients.models import Client
from typing import List


@pytest.mark.django_db
class TestClientViews:
    """Tests for Client-related views including listing and detail pages"""

    def test_client_list_view(self, client: DjangoTestClient) -> None:
        """Verify the client list renders correctly and handles pagination"""
        for i in range(9):
            Client.objects.create(name=f"Client {i}")

        url: str = reverse('clients:list')
        response: TemplateResponse = client.get(url)

        assert response.status_code == 200

        clients_list: List[Client] = list(response.context['clients'])
        assert len(clients_list) == 8

    def test_client_detail_view(self, client: DjangoTestClient) -> None:
        """Verify the client detail page displays the correct object"""
        target: Client = Client.objects.create(name="Target Client")

        url: str = reverse('clients:detail', kwargs={'pk': target.pk})
        response: TemplateResponse = client.get(url)

        assert response.status_code == 200

        context_client: Client = response.context['client']
        assert context_client.name == "Target Client"