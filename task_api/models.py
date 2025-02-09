"""
Этот модуль содержит модель `Tasks`, которая используется для управления задачами,
создаваемыми пользователями в приложении.
Каждая задача включает в себя название, описание, срок выполнения и связь с конкретным пользователем.

Основные компоненты:

- Модель `Tasks`:
    - `title` (CharField): Название задачи с максимальной длиной 200 символов.
    - `description` (TextField): Подробное описание задачи.
    - `due_date` (DateTimeField): Срок выполнения задачи, по умолчанию устанавливается на текущее время.
    - `user` (ForeignKey): Связь с моделью пользователя, указывающая, какому пользователю принадлежит задача.

Мета-класс:
- `verbose_name`: имя модели в единственном числе ("Задача").
- `verbose_name_plural`: имя модели во множественном числе ("Задачи").

Методы:
- `__str__()`: Возвращает строковое представление задачи, представляя её название.

Пример использования:
    task = Tasks.objects.create(
        title="Новая задача",
        description="Описание задачи",
        due_date=timezone.now(),
        user=request.user
    )
    print(task)  # Вывод: "Новая задача"
"""


from django.db import models
from django.utils import timezone
from django.conf import settings

class Tasks(models.Model):
    """
    Модель для представления задач.

    Эта модель используется для хранения информации о задачах, которые создаются пользователями.
    Каждая задача содержит название, описание, срок выполнения и привязку к пользователю.

    Поля:
        - title (CharField): Название задачи. Максимальная длина — 200 символов.
        - description (TextField): Подробное описание задачи.
        - due_date (DateTimeField): Срок выполнения задачи. По умолчанию устанавливается текущая дата и время.
        - user (ForeignKey): Связь с моделью пользователя (User). Задача принадлежит одному пользователю.

    Мета-класс:
        - verbose_name: Человекочитаемое имя модели в единственном числе ("Задача").
        - verbose_name_plural: Человекочитаемое имя модели во множественном числе ("Задачи").

    Методы:
        - __str__(): Возвращает строковое представление задачи (название задачи).

    Пример использования:
        task = Tasks.objects.create(
            title="Новая задача",
            description="Описание задачи",
            due_date=timezone.now(),
            user=request.user
        )
        print(task)  # Вывод: "Новая задача"
    """
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