import pytest
from django.urls import reverse, resolve, ResolverMatch
from django.contrib.staticfiles.storage import staticfiles_storage
from django.test import Client as DjangoTestClient
from typing import Any, Final


@pytest.mark.django_db
class TestGlobalURLs:
    """Integration tests to verify the routing of the entire project"""

    @pytest.mark.parametrize("url_name, expected_status", [
        ('dashboard', 200),
        ('admin:login', 200),
        ('clients:list', 200),
        ('projects:list', 200),
    ])
    def test_main_endpoints_accessible(
            self,
            client: DjangoTestClient,
            url_name: str,
            expected_status: int
    ) -> None:
        """Verify that main sections are accessible by their URL names"""
        url: str = reverse(url_name)
        response: Any = client.get(url)
        assert response.status_code == expected_status

    def test_favicon_redirection(self, client: DjangoTestClient) -> None:
        """Verify that /favicon.ico correctly redirects to the static file"""
        url: Final[str] = '/favicon.ico'
        response: Any = client.get(url)

        assert response.status_code == 302

        expected_static_url: str = staticfiles_storage.url('favicon.ico')
        assert expected_static_url in response.url

    def test_invalid_url_returns_404(self, client: DjangoTestClient) -> None:
        """Verify that non-existent URLs return a 404 Not Found status"""
        response: Any = client.get('/some-random-page-that-does-not-exist/')
        assert response.status_code == 404

    def test_url_resolving(self) -> None:
        """Verify that URL paths resolve to the expected view names and namespaces"""
        resolver: ResolverMatch = resolve('/')
        assert resolver.view_name == 'dashboard'

        resolver_admin: ResolverMatch = resolve('/admin/login/')
        assert 'admin' in str(resolver_admin.app_name)