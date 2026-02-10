import pytest
from django.urls import reverse
from tasks.models import Task


@pytest.mark.django_db
class TestTaskViews:

    def test_task_create_view_post(self, client, project):
        """Checking the creation of a task and linking it to a specific project"""
        url = reverse('tasks:create', kwargs={'project_id': project.pk})
        data = {
            'title': 'Новая задача из вьюхи',
            'status': 'todo',
            'deadline': '2026-12-31'
        }
        response = client.post(url, data)

        # Checking the redirect to the project page
        assert response.status_code == 302
        assert response.url == reverse('projects:detail', kwargs={'pk': project.pk})

        # We check that the task was created and the project is linked correctly.
        task = Task.objects.get(title='Новая задача из вьюхи')
        assert task.project == project

    def test_task_update_view(self, client, project):
        """Checking if an existing task is updated"""
        task = Task.objects.create(title="Старое имя", project=project)
        url = reverse('tasks:update', kwargs={'pk': task.pk})
        data = {
            'title': 'Обновленное имя',
            'status': 'in_progress'
        }

        response = client.post(url, data)
        task.refresh_from_db()

        assert response.status_code == 302
        assert task.title == 'Обновленное имя'
        assert task.status == 'in_progress'

    def test_task_detail_view(self, client, project):
        """Checking the display of task details"""
        task = Task.objects.create(title="Детальная задача", project=project)
        url = reverse('tasks:detail', kwargs={'pk': task.pk})

        response = client.get(url)

        assert response.status_code == 200
        assert response.context['task'] == task
        assert "Детальная задача" in response.content.decode('utf-8')

    def test_task_delete_view_post(self, client, project):
        """Checking task deletion (via POST only)"""
        task = Task.objects.create(title="На удаление", project=project)
        url = reverse('tasks:delete', kwargs={'pk': task.pk})

        # We try GET - there should be 405 Method Not Allowed (due to @require_POST)
        get_response = client.get(url)
        assert get_response.status_code == 405

        post_response = client.post(url)
        assert post_response.status_code == 302
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_task_create_get_project_not_found(self, client):
        """Checking for a 404 error when the project doesn't exist"""
        url = reverse('tasks:create', kwargs={'project_id': 9999})
        response = client.get(url)
        assert response.status_code == 404