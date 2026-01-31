from django.db import models
from projects.models import Project

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('sent', 'Отправлен'),
        ('paid', 'Оплачен'),
        ('overdue', 'Просрочен'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Проект")
    number = models.CharField(max_length=50, unique=True, verbose_name="Номер счёта")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")
    issue_date = models.DateField(auto_now_add=True, verbose_name="Дата выставления")
    due_date = models.DateField(verbose_name="Срок оплаты")
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True, verbose_name="PDF-файл")

    class Meta:
        verbose_name = "Счёт"
        verbose_name_plural = "Счета"
        ordering = ["-issue_date"]

    def __str__(self):
        return f"Счёт №{self.number} ({self.project})"