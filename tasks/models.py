from django.db import models

from projects.models import Project


class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('done', 'Готово'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Проект", related_name="tasks")
    name = models.CharField(max_length=255, verbose_name="Название задачи")
    description = models.TextField(blank=True, verbose_name="Описание")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name="Статус")
    deadline = models.DateField(blank=True, null=True, verbose_name="Дедлайн")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name