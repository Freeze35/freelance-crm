import pytest
from django.urls import reverse
from projects.models import Project
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestProjectViews:

    def test_project_list_annotations(self, client, project):
        """Checking the count of tasks with different statuses in the project list"""
        # Create tasks with different statuses for our project
        Task.objects.create(project=project, title="T1", status='todo')
        Task.objects.create(project=project, title="T2", status='in_progress')
        Task.objects.create(project=project, title="T3", status='done')

        url = reverse('projects:list')
        response = client.get(url)

        assert response.status_code == 200
        # Extract the project from the context (it's in page_obj)
        project_from_ctx = response.context['page_obj'][0]
        assert project_from_ctx.todo_count == 1
        assert project_from_ctx.in_progress_count == 1
        assert project_from_ctx.done_count == 1
        assert project_from_ctx.total_tasks == 3

    def test_project_create_view_post(self, client, project):
        url = reverse('projects:create')
        data = {
            'name': 'New Project From View',
            'client': project.client.id,
            'status': 'new'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Project.objects.filter(name='New Project From View').exists()

    def test_project_create_initial_client(self, client, project):
        url = reverse('projects:create')
        # Pass the client ID from the fixture
        response = client.get(f"{url}?client={project.client.id}")

        # Check the initial value in the form
        assert response.context['form'].initial['client'] == str(project.client.id)

    def test_project_detail_view(self, client, project):
        """Checking the project details page for tasks"""
        Task.objects.create(project=project, title="Task for Detail", status='todo')

        url = reverse('projects:detail', kwargs={'pk': project.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert 'project' in response.context
        assert response.context['project'].name == project.name
        # Check that the task is in the paginator context
        assert len(response.context['tasks']) == 1

    def test_overdue_tasks_logic(self, client, project):
        """Checking the filtering of overdue tasks"""
        today = timezone.now().date()

        # Overdue task (yesterday)
        Task.objects.create(
            project=project, title="Overdue",
            deadline=today - timedelta(days=1), status='todo'
        )
        # Not expired (tomorrow)
        Task.objects.create(
            project=project, title="Future",
            deadline=today + timedelta(days=1), status='todo'
        )
        # Completed (even if the deadline is yesterday, it should not be in overdue)
        Task.objects.create(
            project=project, title="Done",
            deadline=today - timedelta(days=1), status='done'
        )

        url = reverse('projects:overdue_tasks')
        response = client.get(url)

        assert response.status_code == 200
        assert response.context['total_overdue'] == 1
        assert response.context['page_obj'][0].title == "Overdue"

    def test_project_delete_post(self, client, project):
        """Checking for project deletion"""
        url = reverse('projects:delete', kwargs={'pk': project.pk})
        response = client.post(url)

        assert response.status_code == 302
        assert not Project.objects.filter(pk=project.pk).exists()
