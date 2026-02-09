from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя / Компания")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    notes = models.TextField(blank=True, verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Telegram Chat ID",
        help_text="Личный ID чата клиента в Telegram"
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def formatted_phone(self):
        if self.phone and len(self.phone) == 11:
            return f'+7 {self.phone[1:4]} {self.phone[4:7]} {self.phone[7:]}'
        return self.phone or '—'