from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя / Компания")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=50,blank=True,verbose_name="Телефон")
    notes = models.TextField(blank=True,verbose_name="Заметки")
    created_at = models.DateTimeField(auto_now_add=True,verbose_name="Создан")

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name