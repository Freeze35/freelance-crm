import pytest
from datetime import timedelta
from django.utils import timezone
from tasks.models import Task


@pytest.mark.django_db
class TestTaskModel:

    def test_task_str_representation(self, project):
        """Checking the string display of a task"""
        task = Task.objects.create(
            title="Тестовая задача",
            project=project
        )
        assert str(task) == f"Тестовая задача ({project})"

    def test_is_overdue_property(self, project):
        """Checking the logic for determining an overdue task"""
        today = timezone.now().date()

        #1. The task is overdue (yesterday's deadline, status)
        task_overdue = Task.objects.create(
            title="Просрочена",
            project=project,
            deadline=today - timedelta(days=1),
            status='todo'
        )
        assert task_overdue.is_overdue is True

        #2. The task is not overdue (future deadline)
        task_future = Task.objects.create(
            title="Будущая",
            project=project,
            deadline=today + timedelta(days=1),
            status='todo'
        )
        assert task_future.is_overdue is False

        #3. Deadline is yesterday, but status is 'done' - should not be considered overdue
        task_done = Task.objects.create(
            title="Сделана вчера",
            project=project,
            deadline=today - timedelta(days=1),
            status='done'
        )
        assert task_done.is_overdue is False

        #4. No deadline - not overdue
        task_no_deadline = Task.objects.create(
            title="Без дедлайна",
            project=project,
            deadline=None
        )

        assert bool(task_no_deadline.is_overdue) is False

    def test_task_ordering(self, project):
        """Sort by: first by deadline, then by creation date"""
        today = timezone.now().date()

        # Create a task with a late deadline
        t1 = Task.objects.create(title="Поздняя", project=project, deadline=today + timedelta(days=5))
        # Create a task with an early deadline
        t2 = Task.objects.create(title="Ранняя", project=project, deadline=today + timedelta(days=1))

        tasks = Task.objects.all()
        assert tasks[0] == t2
        assert tasks[1] == t1