import pytest
from django.urls import reverse
from django.utils import timezone
from django.test import Client as DjangoTestClient
from django.template.response import TemplateResponse
from datetime import timedelta, date
from typing import Final, Any

from clients.models import Client
from projects.models import Project
from tasks.models import Task


@pytest.mark.django_db
class TestDashboardView:
    """Tests for the main dashboard view and its statistical calculations"""

    def test_dashboard_context_data(self, client: DjangoTestClient) -> None:
        """Verify the accuracy of statistics calculations on the dashboard"""

        # 1. Create a base client for relationship mapping
        test_client: Client = Client.objects.create(name="Test Client")

        # 2. Create projects with different statuses linked to the client
        Project.objects.create(name="P1", status='new', client=test_client)
        Project.objects.create(name="P2", status='in_progress', client=test_client)
        Project.objects.create(name="P3", status='completed', client=test_client)
        Project.objects.create(name="P4", status='canceled', client=test_client)

        # 3. Create a specific project for task assignment
        p_for_task: Project = Project.objects.create(
            name="Task Project",
            status='new',
            client=test_client
        )

        # Setup dates for task deadline testing
        today_date: date = timezone.now().date()
        yesterday: Final[date] = today_date - timedelta(days=1)
        tomorrow: Final[date] = today_date + timedelta(days=1)

        # Create tasks with various statuses and deadlines
        Task.objects.create(title="Overdue", status='todo', deadline=yesterday, project=p_for_task)
        Task.objects.create(title="Future", status='todo', deadline=tomorrow, project=p_for_task)
        Task.objects.create(title="Done but old", status='completed', deadline=yesterday, project=p_for_task)

        # 4. Execute the GET request to the dashboard
        url: str = reverse('dashboard')
        response: TemplateResponse | Any = client.get(url)

        # 5. Validation of status code and context statistics
        assert response.status_code == 200
        assert response.context['client_count'] == 1

        # Total projects should exclude 'canceled' status (P1, P2, P3 + Task Project = 4)
        assert response.context['project_total'] == 4

        # Only incomplete tasks with past deadlines should be counted as overdue
        assert response.context['overdue_tasks'] == 1