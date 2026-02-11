from django.db import models
from clients.models import Client
from typing import List, Tuple

class Project(models.Model):
    """
        Represents a specific work engagement with a Client.

        The Project model acts as a central hub for tasks and invoices.
        It tracks financial goals (budget), time constraints (deadline),
        and the current stage of the workflow.

        Attributes:
            name: The title of the project.
            client: ForeignKey linking the project to a specific Client.
            description: Detailed scope of work.
            budget: Total monetary value assigned to the project.
            status: Current phase (new, in_progress, done, canceled).
            deadline: Targeted completion date.
            created_at: Automatic timestamp of project initialization.
    """

    STATUS_CHOICES: List[Tuple[str, str]] = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('done', 'Завершён'),
        ('canceled', 'Отменён'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название проекта")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects', verbose_name="Клиент")
    description = models.TextField(blank=True, verbose_name="Описание")
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Бюджет")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    deadline = models.DateField(blank=True, null=True, verbose_name="Дедлайн")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return the project name and its associated client as a string"""
        return f"{self.name} ({self.client})"