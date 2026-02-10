import pytest
from django.urls import reverse
from django.test import Client as DjangoTestClient
from django.template.response import TemplateResponse
from typing import Any, Dict, Final
from tasks.models import Task
from projects.models import Project


@pytest.mark.django_db
class TestTaskViews:

    def test_task_create_view_post(self, client: DjangoTestClient, project: Project) -> None:
        """Verify task creation and automatic association with a project via POST"""
        url: str = reverse('tasks:create', kwargs={'project_id': project.pk})
        data: Dict[str, str] = {
            'title': 'Новая задача из вьюхи',
            'status': 'todo',
            'deadline': '2026-12-31'
        }
        response: Any = client.post(url, data)

        # Ensure redirect points to the project detail page
        expected_redirect: str = reverse('projects:detail', kwargs={'pk': project.pk})
        assert response.status_code == 302
        assert response.url == expected_redirect

        # Verify database integrity and relationship
        task: Task = Task.objects.get(title='Новая задача из вьюхи')
        assert task.project == project

    def test_task_update_view(self, client: DjangoTestClient, project: Project) -> None:
        """Verify that an existing task's attributes are correctly updated"""
        task: Task = Task.objects.create(title="Старое имя", project=project)
        url: str = reverse('tasks:update', kwargs={'pk': task.pk})
        data: Dict[str, str] = {
            'title': 'Обновленное имя',
            'status': 'in_progress'
        }

        response: Any = client.post(url, data)
        task.refresh_from_db()

        assert response.status_code == 302
        assert task.title == 'Обновленное имя'
        assert task.status == 'in_progress'

    def test_task_detail_view(self, client: DjangoTestClient, project: Project) -> None:
        """Verify the task detail page loads correctly and displays task data"""
        task: Task = Task.objects.create(title="Детальная задача", project=project)
        url: str = reverse('tasks:detail', kwargs={'pk': task.pk})

        response: TemplateResponse | Any = client.get(url)

        assert response.status_code == 200
        assert response.context['task'] == task
        assert "Детальная задача" in response.content.decode('utf-8')

    def test_task_delete_view_post(self, client: DjangoTestClient, project: Project) -> None:
        """Verify task deletion is restricted to POST and removes the record"""
        task: Task = Task.objects.create(title="На удаление", project=project)
        task_pk: int = task.pk
        url: str = reverse('tasks:delete', kwargs={'pk': task_pk})

        # Ensure GET request is rejected (405 Method Not Allowed)
        get_response: Any = client.get(url)
        assert get_response.status_code == 405

        # Ensure POST request deletes the task
        post_response: Any = client.post(url)
        assert post_response.status_code == 302
        assert not Task.objects.filter(pk=task_pk).exists()

    def test_task_create_get_project_not_found(self, client: DjangoTestClient) -> None:
        """Verify a 404 response when attempting to create a task for a non-existent project"""
        invalid_project_id: Final[int] = 9999
        url: str = reverse('tasks:create', kwargs={'project_id': invalid_project_id})
        response: Any = client.get(url)

        assert response.status_code == 404