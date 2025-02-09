"""
Модуль для работы с сериализаторами в Django REST Framework.

Этот модуль содержит сериализаторы, которые используются для преобразования данных
между моделями Django и форматами, пригодными для передачи по API (например, JSON).
Сериализаторы также выполняют валидацию данных и управляют созданием и обновлением объектов.

Содержание модуля:
1. UserRegistrationSerializer:
   - Сериализатор для регистрации новых пользователей.
   - Включает поля `username`, `email` и `password`.
   - Пароль валидируется на минимальную длину (8 символов) и хэшируется при создании пользователя.

2. TaskSerializer:
   - Сериализатор для работы с задачами (Tasks).
   - Автоматически привязывает задачу к текущему пользователю при создании.
   - Поле `user` доступно только для чтения.

3. UserSerializer:
   - Сериализатор для представления данных пользователя.
   - Возвращает поля `id`, `username`, `email` и `is_staff`.

Примеры использования:
- Регистрация нового пользователя:
    serializer = UserRegistrationSerializer(data={
        'username': 'new_user',
        'email': 'user@example.com',
        'password': 'securepassword123'
    })
    if serializer.is_valid():
        user = serializer.save()

- Создание задачи:
    serializer = TaskSerializer(data={
        'title': 'Новая задача',
        'description': 'Описание задачи',
        'due_date': '2023-12-31'
    }, context={'request': request})
    if serializer.is_valid():
        task = serializer.save()

- Получение данных пользователя:
    user = User.objects.get(id=1)
    serializer = UserSerializer(user)
    print(serializer.data)
    # Output: {'id': 1, 'username': 'john_doe', 'email': 'john@example.com', 'is_staff': False}
"""

from rest_framework import serializers
from django.contrib.auth.models import User

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from .models import Tasks

User = get_user_model()

class UserRegistrationSerializer(ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.

    Этот сериализатор используется для валидации и создания нового пользователя.
    Он включает поля `username`, `email` и `password`, где `password` является write-only
    (не возвращается в ответе) и должен содержать минимум 8 символов.

    Атрибуты:
        password (CharField): Поле для пароля. Только для записи, минимальная длина — 8 символов.

    Мета-класс:
        model (User): Модель, с которой работает сериализатор.
        fields (tuple): Поля, которые используются в сериализаторе (`username`, `email`, `password`).
        extra_kwargs (dict): Дополнительные параметры для полей. Например, `email` является обязательным.

    Методы:
        validate_password(value): Валидирует пароль, проверяя его длину.
        create(validated_data): Создает нового пользователя с хэшированным паролем.

    Пример использования:
        serializer = UserRegistrationSerializer(data={
            'username': 'new_user',
            'email': 'user@example.com',
            'password': 'securepassword123'
        })
        if serializer.is_valid():
            user = serializer.save()
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'email': {'required': True},  # Делаем email обязательным полем
        }

    def validate_password(self, value):
        """
        Метод валидирует пароль.

        Проверяет, что пароль содержит минимум 8 символов.

        Аргументы:
            value (str): Пароль, который нужно валидировать.

        Возвращает:
            str: Валидный пароль.

        Исключения:
            ValidationError: Если пароль короче 8 символов.
        """
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов.")
        return value

    def create(self, validated_data):
        """
        Создает нового пользователя с хэшированным паролем.

        Аргументы:
            validated_data (dict): Валидированные данные для создания пользователя.

        Возвращает:
            User: Созданный объект пользователя.
        """
        user = User.objects.create_user(**validated_data)
        return user


class TaskSerializer(ModelSerializer):
    """
    Сериализатор для модели задачи (Tasks).

    Этот сериализатор используется для создания и представления задач.
    Поле `user` автоматически привязывается к текущему пользователю при создании задачи
    и является read-only (не может быть изменено вручную).

    Мета-класс:
        model (Tasks): Модель, с которой работает сериализатор.
        fields (tuple): Поля, которые используются в сериализаторе (`id`, `title`, `description`, `due_date`, `user`).
        read_only_fields (tuple): Поля, доступные только для чтения (`id`, `user`).

    Методы:
        create(validated_data): Создает новую задачу, автоматически привязывая ее к текущему пользователю.

    Пример использования:
        serializer = TaskSerializer(data={
            'title': 'Новая задача',
            'description': 'Описание задачи',
            'due_date': '2023-12-31'
        }, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
    """
    class Meta:
        model = Tasks
        fields = ('id', 'title', 'description', 'due_date', 'user')
        read_only_fields = ('id', 'user')  # Поле 'user' будет автоматически заполняться

    def create(self, validated_data):
        """
        Создает новую задачу, автоматически привязывая ее к текущему пользователю.

        Аргументы:
            validated_data (dict): Валидированные данные для создания задачи.

        Возвращает:
            Tasks: Созданный объект задачи.

        Примечание:
            Поле `user` заполняется автоматически на основе текущего пользователя,
            который содержится в контексте запроса (`self.context['request'].user`).
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели пользователя (User).

    Этот сериализатор используется для представления данных пользователя.
    Он возвращает следующие поля:
    - `id`: Уникальный идентификатор пользователя.
    - `username`: Имя пользователя.
    - `email`: Электронная почта пользователя.
    - `is_staff`: Флаг, указывающий, является ли пользователь сотрудником (staff).

    Мета-класс:
        model (User): Модель, с которой работает сериализатор.
        fields (tuple): Поля, которые возвращаются в ответе (`id`, `username`, `email`, `is_staff`).

    Пример использования:
        user = User.objects.get(id=1)
        serializer = UserSerializer(user)
        print(serializer.data)
        # Output: {'id': 1, 'username': 'john_doe', 'email': 'john@example.com', 'is_staff': False}
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff')  # Поля, которые будут возвращаться