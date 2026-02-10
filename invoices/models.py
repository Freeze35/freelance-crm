from django.db import models
from projects.models import Project
from django.utils import timezone
from typing import List, Tuple

class Invoice(models.Model):
    STATUS_CHOICES: List[Tuple[str, str]] = [
        ('draft', 'Черновик'),
        ('sent', 'Отправлен'),
        ('paid', 'Оплачен'),
        ('partially_paid', 'Частично оплачен'),
        ('overdue', 'Просрочен'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')
    number = models.CharField(max_length=50, unique=True, verbose_name="Номер счёта")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма")
    issue_date = models.DateField(default=timezone.now, verbose_name="Дата выставления")
    due_date = models.DateField(verbose_name="Срок оплаты")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Счёт"
        verbose_name_plural = "Счета"
        ordering = ['-created_at', '-id']

    def __str__(self) -> str:
        """Return a formatted string representation of the invoice"""
        return f"Счёт {self.number} — {self.project.name}"