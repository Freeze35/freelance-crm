from django.db import models
from clients.models import Client

class Project(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('done', 'Завершён'),
        ('canceled', 'Отменён'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название проекта")
    client = models.ForeignKey(Client, on_delete=models.CASCADE,related_name='projects', verbose_name="Клиент")
    description = models.TextField(blank=True, verbose_name="Описание")
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Бюджет")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    deadline = models.DateField(blank=True, null=True, verbose_name="Дедлайн")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.client})"