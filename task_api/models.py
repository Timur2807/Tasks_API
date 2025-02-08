from django.db import models
from django.utils import timezone
from django.conf import settings

class Tasks(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название Задачи")
    description = models.TextField(verbose_name="Описание Задачи")
    due_date = models.DateTimeField(default=timezone.now, verbose_name="Срок выполнения")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="tasks", verbose_name="Пользователь")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self):
        return self.title