import pytest
from django.urls import reverse, resolve
from django.contrib.staticfiles.storage import staticfiles_storage


@pytest.mark.django_db
class TestGlobalURLs:
    """Integration tests to verify the routing of the entire project"""

    @pytest.mark.parametrize("url_name, expected_status", [
        ('dashboard', 200),
        ('admin:login', 200),
        ('clients:list', 200),
        ('projects:list', 200),
    ])
    def test_main_endpoints_accessible(self, client, url_name, expected_status):
        """Checking the availability of all main sections by their names"""
        url = reverse(url_name)
        response = client.get(url)
        assert response.status_code == expected_status

    def test_favicon_redirection(self, client):
        """Checking that favicon.ico correctly redirects to a static file"""
        url = '/favicon.ico'
        response = client.get(url)

        # Check that this is a redirect
        assert response.status_code == 302
        # We check that it leads to statics
        assert staticfiles_storage.url('favicon.ico') in response.url

    def test_invalid_url_returns_404(self, client):
        """Checking if a non-existent URL returns 404"""
        response = client.get('/some-random-page-that-does-not-exist/')
        assert response.status_code == 404

    def test_url_resolving(self):
        """Checking that URLs point to the correct views (Resolve)"""
        # This ensures that the '/' path actually calls the dashboard
        resolver = resolve('/')
        assert resolver.view_name == 'dashboard'

        resolver_admin = resolve('/admin/login/')
        assert 'admin' in resolver_admin.app_name
