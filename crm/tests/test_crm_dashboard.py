import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from clients.models import Client
from projects.models import Project
from tasks.models import Task


@pytest.mark.django_db
class TestDashboardView:

    def test_dashboard_context_data(self, client):
        "Checking the accuracy of statistics calculations on the dashboard"""
        # 1. First, create a client
        test_client = Client.objects.create(name="Test Client")

        # 2. We pass this client to each project via the client=test_client argument
        Project.objects.create(name="P1", status='new', client=test_client)
        Project.objects.create(name="P2", status='in_progress', client=test_client)
        Project.objects.create(name="P3", status='completed', client=test_client)
        Project.objects.create(name="P4", status='canceled', client=test_client)

        # 3. For tasks, you also need to create a project, since tasks are linked to it
        p_for_task = Project.objects.create(name="Task Project", status='new', client=test_client)

        yesterday = timezone.now().date() - timedelta(days=1)
        tomorrow = timezone.now().date() + timedelta(days=1)

        # Don't forget to add project=p_for_task when creating tasks
        Task.objects.create(title="Overdue", status='todo', deadline=yesterday, project=p_for_task)
        Task.objects.create(title="Future", status='todo', deadline=tomorrow, project=p_for_task)
        Task.objects.create(title="Done but old", status='completed', deadline=yesterday, project=p_for_task)

        # 4. Execute the request
        url = reverse('dashboard')
        response = client.get(url)

        # 5. Checks
        assert response.status_code == 200
        assert response.context['client_count'] == 1
        # We now have 5 projects (P1, P2, P3, P4 + p_for_task),
        # P4 is canceled, so the total should be 4
        assert response.context['project_total'] == 4
        assert response.context['overdue_tasks'] == 1
