from django.db import models
from projects.models import Project
from django.utils import timezone
from typing import List, Tuple

class Invoice(models.Model):
    """
        Represents a financial document issued to a client for project work.

        The Invoice model tracks the billing amount, payment deadlines, and
        the current lifecycle status of a payment request.

        Attributes:
            project: Reference to the associated Project.
            number: Unique identifier for the invoice (e.g., INV-2026-001).
            amount: The total monetary value of the invoice.
            issue_date: The date when the invoice was generated.
            due_date: The deadline for the payment.
            status: The current state of the invoice (draft, sent, paid, etc.).
        """

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