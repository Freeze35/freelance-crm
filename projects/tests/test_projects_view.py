import pytest
from django.urls import reverse
from django.test import Client as DjangoTestClient
from django.template.response import TemplateResponse
from projects.models import Project
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta, date
from typing import Any, Dict, Final

@pytest.mark.django_db
class TestProjectViews:

    def test_project_list_annotations(self, client: DjangoTestClient, project: Project) -> None:
        """Verify task status counts within the project list context"""
        Task.objects.create(project=project, title="T1", status='todo')
        Task.objects.create(project=project, title="T2", status='in_progress')
        Task.objects.create(project=project, title="T3", status='done')

        url: str = reverse('projects:list')
        response: TemplateResponse | Any = client.get(url)

        assert response.status_code == 200
        project_from_ctx: Any = response.context['page_obj'][0]
        assert project_from_ctx.todo_count == 1
        assert project_from_ctx.in_progress_count == 1
        assert project_from_ctx.done_count == 1
        assert project_from_ctx.total_tasks == 3

    def test_project_create_view_post(self, client: DjangoTestClient, project: Project) -> None:
        """Verify project creation via POST request"""
        url: str = reverse('projects:create')
        data: Dict[str, Any] = {
            'name': 'New Project From View',
            'client': project.client.pk,
            'status': 'new'
        }
        response: Any = client.post(url, data)
        assert response.status_code == 302
        assert Project.objects.filter(name='New Project From View').exists()

    def test_project_create_initial_client(self, client: DjangoTestClient, project: Project) -> None:
        """Verify the initial client value in the creation form via GET parameters"""
        url: str = reverse('projects:create')
        client_id: int = project.client.pk
        response: TemplateResponse | Any = client.get(f"{url}?client={client_id}")

        assert response.context['form'].initial['client'] == str(client_id)

    def test_project_detail_view(self, client: DjangoTestClient, project: Project) -> None:
        """Verify the project detail page content and task presence"""
        Task.objects.create(project=project, title="Task for Detail", status='todo')

        url: str = reverse('projects:detail', kwargs={'pk': project.pk})
        response: TemplateResponse | Any = client.get(url)

        assert response.status_code == 200
        assert 'project' in response.context
        assert response.context['project'].name == project.name
        assert len(response.context['tasks']) == 1

    def test_overdue_tasks_logic(self, client: DjangoTestClient, project: Project) -> None:
        """Verify the filtering logic for overdue tasks across projects"""
        today: date = timezone.now().date()

        Task.objects.create(
            project=project, title="Overdue",
            deadline=today - timedelta(days=1), status='todo'
        )
        Task.objects.create(
            project=project, title="Future",
            deadline=today + timedelta(days=1), status='todo'
        )
        Task.objects.create(
            project=project, title="Done",
            deadline=today - timedelta(days=1), status='done'
        )

        url: str = reverse('projects:overdue_tasks')
        response: TemplateResponse | Any = client.get(url)

        assert response.status_code == 200
        assert response.context['total_overdue'] == 1
        assert response.context['page_obj'][0].title == "Overdue"

    def test_project_delete_post(self, client: DjangoTestClient, project: Project) -> None:
        """Verify successful project deletion via POST"""
        project_pk: int = project.pk
        url: str = reverse('projects:delete', kwargs={'pk': project_pk})
        response: Any = client.post(url)

        assert response.status_code == 302
        assert not Project.objects.filter(pk=project_pk).exists()