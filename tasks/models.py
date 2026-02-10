from django.db import models
from projects.models import Project
from django.utils import timezone
from typing import List, Tuple, Optional
from datetime import date

class Task(models.Model):
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
        """Return the task title and its associated project name"""
        return f"{self.title} ({self.project})"

    @property
    def is_overdue(self) -> bool:
        """Check if the task is past its deadline and not yet completed"""
        current_date: date = timezone.now().date()
        return bool(
            self.deadline and
            self.deadline < current_date and
            self.status != 'done'
        )