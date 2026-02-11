from django.db import models
from projects.models import Project
from django.utils import timezone
from typing import List, Tuple, Optional
from datetime import date

class Task(models.Model):
    """
        Represents an atomic unit of work within a Project.

        Tasks track specific actions, their current state, and deadlines.
        They are the primary source for the 'Overdue' monitoring system.

        Attributes:
            project: ForeignKey linking to the parent Project.
            title: Short summary of the task.
            description: Detailed instructions or notes.
            status: Current state.
            deadline: The date by which the task should be finished.
            created_at: Automatic timestamp of task creation.
    """
    STATUS_CHOICES: List[Tuple[str, str]] = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('done', 'Завершена'),
        ('canceled', 'Отменена'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255, verbose_name="Название задачи")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name="Статус")
    deadline = models.DateField(null=True, blank=True, verbose_name="Дедлайн")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['deadline', '-created_at']

    def __str__(self) -> str:
        """Return the task title and its associated project name."""
        return f"{self.title} ({self.project})"

    @property
    def is_overdue(self) -> bool:
        """
        Determines if the task is overdue.

        A task is considered overdue if:
        1. It has a deadline set.
        2. The deadline is earlier than the current date.
        3. The status is not 'done'.

        Returns:
            bool: True if the task is overdue, False otherwise.
        """
        current_date: date = timezone.now().date()
        return bool(
            self.deadline and
            self.deadline < current_date and
            self.status != 'done'
        )