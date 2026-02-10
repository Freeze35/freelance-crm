import pytest
from datetime import timedelta, date
from django.utils import timezone
from tasks.models import Task
from projects.models import Project

@pytest.mark.django_db
class TestTaskModel:

    def test_task_str_representation(self, project: Project) -> None:
        """Verify the task's string representation includes title and project"""
        task: Task = Task.objects.create(
            title="Тестовая задача",
            project=project
        )
        assert str(task) == f"Тестовая задача ({project})"

    def test_is_overdue_property(self, project: Project) -> None:
        """Verify the logic for the is_overdue property under various conditions"""
        today: date = timezone.now().date()

        # 1. Overdue: past deadline and incomplete status
        task_overdue: Task = Task.objects.create(
            title="Просрочена",
            project=project,
            deadline=today - timedelta(days=1),
            status='todo'
        )
        assert task_overdue.is_overdue is True

        # 2. Not overdue: future deadline
        task_future: Task = Task.objects.create(
            title="Будущая",
            project=project,
            deadline=today + timedelta(days=1),
            status='todo'
        )
        assert task_future.is_overdue is False

        # 3. Not overdue: past deadline but status is 'done'
        task_done: Task = Task.objects.create(
            title="Сделана вчера",
            project=project,
            deadline=today - timedelta(days=1),
            status='done'
        )
        assert task_done.is_overdue is False

        # 4. Not overdue: no deadline provided
        task_no_deadline: Task = Task.objects.create(
            title="Без дедлайна",
            project=project,
            deadline=None
        )
        assert bool(task_no_deadline.is_overdue) is False

    def test_task_ordering(self, project: Project) -> None:
        """Verify tasks are ordered by deadline (ascending) by default"""
        today: date = timezone.now().date()

        # Task with a later deadline
        t1: Task = Task.objects.create(title="Поздняя", project=project, deadline=today + timedelta(days=5))
        # Task with an earlier deadline
        t2: Task = Task.objects.create(title="Ранняя", project=project, deadline=today + timedelta(days=1))

        tasks = Task.objects.all()
        assert tasks[0] == t2
        assert tasks[1] == t1