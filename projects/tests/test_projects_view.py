import pytest
from django.urls import reverse
from projects.models import Project
from tasks.models import Task
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestProjectViews:

    def test_project_list_annotations(self, client, project):
        """Проверка подсчета задач разных статусов в списке проектов"""
        # Создаем задачи с разными статусами для нашего проекта
        Task.objects.create(project=project, title="T1", status='todo')
        Task.objects.create(project=project, title="T2", status='in_progress')
        Task.objects.create(project=project, title="T3", status='done')

        url = reverse('projects:list')
        response = client.get(url)

        assert response.status_code == 200
        # Достаем проект из контекста (он в page_obj)
        project_from_ctx = response.context['page_obj'][0]
        assert project_from_ctx.todo_count == 1
        assert project_from_ctx.in_progress_count == 1
        assert project_from_ctx.done_count == 1
        assert project_from_ctx.total_tasks == 3

    def test_project_create_view_post(self, client, project): # Заменили client_instance на project
        url = reverse('projects:create')
        data = {
            'name': 'New Project From View',
            'client': project.client.id, # Берем ID клиента из существующего проекта
            'status': 'new'
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Project.objects.filter(name='New Project From View').exists()

    def test_project_create_initial_client(self, client, project):  # Заменили client_instance на project
        url = reverse('projects:create')
        # Передаем ID клиента из фикстуры
        response = client.get(f"{url}?client={project.client.id}")

        # Проверяем начальное значение в форме
        assert response.context['form'].initial['client'] == str(project.client.id)

    def test_project_detail_view(self, client, project):
        """Проверка страницы деталей проекта и наличия в ней задач"""
        Task.objects.create(project=project, title="Task for Detail", status='todo')

        url = reverse('projects:detail', kwargs={'pk': project.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert 'project' in response.context
        assert response.context['project'].name == project.name
        # Проверяем, что задача попала в контекст пагинатора
        assert len(response.context['tasks']) == 1

    def test_overdue_tasks_logic(self, client, project):
        """Проверка фильтрации просроченных задач"""
        today = timezone.now().date()

        # Просроченная задача (вчера)
        Task.objects.create(
            project=project, title="Overdue",
            deadline=today - timedelta(days=1), status='todo'
        )
        # Не просроченная (завтра)
        Task.objects.create(
            project=project, title="Future",
            deadline=today + timedelta(days=1), status='todo'
        )
        # Завершенная (даже если дедлайн вчера, она не должна быть в overdue)
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
        """Проверка удаления проекта"""
        url = reverse('projects:delete', kwargs={'pk': project.pk})
        response = client.post(url)  # POST запрос удаляет

        assert response.status_code == 302
        assert not Project.objects.filter(pk=project.pk).exists()