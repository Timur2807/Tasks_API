"""
Модуль views для Django REST Framework.

Этот модуль содержит представления (views) для работы с пользователями и задачами.
Он обеспечивает регистрацию пользователей, управление задачами и доступ к данным пользователей.

Основные компоненты модуля:
1. UserRegistrationView:
   - Представление для регистрации новых пользователей.
   - Использует `UserRegistrationSerializer` для валидации и создания пользователей.
   - Доступно всем пользователям (permissions.AllowAny).

2. TaskViewSet:
   - ViewSet для работы с задачами (Tasks).
   - Обеспечивает создание, чтение, обновление и удаление задач.
   - Задачи автоматически привязываются к текущему пользователю.
   - Доступно только аутентифицированным пользователям (IsAuthenticated).
   - Поддерживает фильтрацию, поиск и сортировку задач.

3. UserViewSet:
   - ViewSet для работы с пользователями (User).
   - Обеспечивает просмотр списка пользователей и их деталей для аутентифицированных пользователей.
   - Создание, обновление и удаление пользователей доступно только администраторам (IsAdminUser).

Примеры использования:
- Регистрация нового пользователя:
    POST /api/register/
    {
        "username": "new_user",
        "email": "user@example.com",
        "password": "securepassword123"
    }

- Получение списка задач:
    GET /api/tasks/

- Создание новой задачи:
    POST /api/tasks/
    {
        "title": "Новая задача",
        "description": "Описание задачи",
        "due_date": "2023-12-31"
    }

- Получение списка пользователей:
    GET /api/users/

- Создание нового пользователя (только для администраторов):
    POST /api/users/
    {
        "username": "admin_user",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "is_staff": true
    }
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer
from django.contrib.auth import get_user_model
from .models import Tasks
from rest_framework import viewsets, status
from .serializers import TaskSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
import logging


logger = logging.getLogger(__name__)



logger = logging.getLogger(__name__)
class UserRegistrationView(generics.CreateAPIView):
    """
    Представление для регистрации нового пользователя.

    Это представление позволяет любому пользователю зарегистрироваться в системе.
    Оно использует сериализатор `UserRegistrationSerializer` для валидации данных
    и создания нового пользователя.

    Атрибуты:
        serializer_class (Serializer): Сериализатор, используемый для валидации и создания пользователя.
        permission_classes (list): Список классов разрешений. По умолчанию разрешено всем (`AllowAny`).

    Методы:
        post(request, *args, **kwargs): Обрабатывает POST-запрос для регистрации пользователя.

    Пример запроса:
        POST /api/register/
        {
            "username": "new_user",
            "email": "user@example.com",
            "password": "securepassword123"
        }

    Пример ответа:
        {
            "user": {
                "id": 1,
                "username": "new_user",
                "email": "user@example.com"
            },
            "message": "User created successfully."
        }
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Разрешить регистрацию всем

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для регистрации нового пользователя.

        Аргументы:
            request (Request): Объект запроса, содержащий данные пользователя.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Возвращает:
            Response: Ответ с данными зарегистрированного пользователя и сообщением об успешной регистрации.

        Исключения:
            ValidationError: Если данные не прошли валидацию.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserRegistrationSerializer(user, context=self.get_serializer_context()).data,
            "message": "User created successfully.",
        })




class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с задачами (Tasks).

    Обеспечивает следующие действия:
    - `list`: Возвращает список задач, созданных текущим пользователем.
    - `retrieve`: Возвращает детали конкретной задачи.
    - `create`: Создает новую задачу, автоматически привязывая её к текущему пользователю.
    - `update`: Обновляет данные задачи. Доступно только для владельца задачи.
    - `partial_update`: Частично обновляет данные задачи. Доступно только для владельца задачи.
    - `destroy`: Удаляет задачу. Доступно только для владельца задачи.

    Поля, возвращаемые в API:
    - `id`: Уникальный идентификатор задачи.
    - `title`: Название задачи.
    - `description`: Описание задачи.
    - `due_date`: Срок выполнения задачи.
    - `user`: Пользователь, создавший задачу.

    Права доступа:
    - Только аутентифицированные пользователи могут выполнять любые действия с задачами.
    - Пользователь может работать только с задачами, которые он создал.

    Фильтрация, поиск и сортировка:
    - `search_fields`: Поиск по полям `title`, `description`, `due_date`, `user`.
    - `filterset_fields`: Фильтрация по полям `title`, `description`, `due_date`, `user`.
    - `ordering_fields`: Сортировка по полям `due_date`, `user`.

    Кэширование:
    - GET-запросы кэшируются с использованием Redis.
    - Кэш очищается при создании, обновлении или удалении задачи.
    """
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]  # Только аутентифицированные пользователи
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    # Отображается поле поиска.
    search_fields = ['title', 'description', 'due_date', 'user']

    # Отображается поле фильтрации.
    filterset_fields = [
        'title',
        'description',
        'due_date',
        'user'
    ]
    # Отображается поле сортировки.
    ordering_fields = [
        'due_date',
        'user',
    ]

    def get_queryset(self):
        """
        Возвращает queryset задач, созданных текущим пользователем.

        Returns:
            QuerySet: Список задач, принадлежащих текущему пользователю.
        """
        logger.info("Запрос задач")
        return self.queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Возвращает список задач, созданных текущим пользователем.
        Результат кэшируется с использованием Redis.

        Returns:
            Response: Список задач в формате JSON.
        """
        cache_key = f'tasks_{request.user.id}'  # Уникальный ключ для кэша
        cached_data = cache.get(cache_key)

        if cached_data:
            logger.info("Данные получены из кэша")
            return Response(cached_data)

        # Если данных нет в кэше, выполняем запрос к базе данных.
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Кэшируем данные на 5 минут (300 секунд)
        cache.set(cache_key, data, timeout=300)
        logger.info("Данные закэшированы")

        return Response(data)

    def perform_create(self, serializer):
        """
        Автоматически привязывает задачу к текущему пользователю при создании.
        Очищает кэш для текущего пользователя.

        Args:
            serializer: Сериализатор для создания задачи.
        """
        serializer.save(user=self.request.user)
        cache_key = f'tasks_{self.request.user.id}'
        cache.delete(cache_key)  # Очищаем кэш после создания задачи
        logger.info("Кэш очищен после создания задачи")

    def update(self, request, *args, **kwargs):
        """
        Обновляет задачу. Доступно только для владельца задачи.
        Очищает кэш для текущего пользователя.

        Args:
            request: Запрос от клиента.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Ответ с обновленными данными задачи или ошибкой 403, если пользователь не является владельцем.
        """
        instance = self.get_object()

        # Проверяем, что текущий пользователь является владельцем задачи
        if instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на обновление этой задачи."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cache_key = f'tasks_{request.user.id}'
        cache.delete(cache_key)  # Очищаем кэш после обновления задачи
        logger.info("Кэш очищен после обновления задачи")

        # Вызываем родительский метод для обновления
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Частично обновляет задачу. Доступно только для владельца задачи.
        Очищает кэш для текущего пользователя.

        Args:
            request: Запрос от клиента.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Ответ с обновленными данными задачи или ошибкой 403, если пользователь не является владельцем.
        """
        instance = self.get_object()

        # Проверяем, что текущий пользователь является владельцем задачи
        if instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на частичное обновление этой задачи."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cache_key = f'tasks_{request.user.id}'
        cache.delete(cache_key)  # Очищаем кэш после частичного обновления задачи
        logger.info("Кэш очищен после частичного обновления задачи")

        # Вызываем родительский метод для частичного обновления
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет задачу. Доступно только для владельца задачи.
        Очищает кэш для текущего пользователя.

        Args:
            request: Запрос от клиента.
            *args: Дополнительные аргументы.
            **kwargs: Дополнительные именованные аргументы.

        Returns:
            Response: Ответ с подтверждением удаления или ошибкой 403, если пользователь не является владельцем.
        """
        instance = self.get_object()

        # Проверяем, что текущий пользователь является владельцем задачи
        if instance.user != request.user:
            return Response(
                {"detail": "У вас нет прав на удаление этой задачи."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cache_key = f'tasks_{request.user.id}'
        cache.delete(cache_key)  # Очищаем кэш после удаления задачи
        logger.info("Кэш очищен после удаления задачи")

        # Вызываем родительский метод для удаления
        return super().destroy(request, *args, **kwargs)

User = get_user_model()
class UserViewSet(viewsets.ModelViewSet):
    """
        ViewSet для работы с пользователями.

        Обеспечивает следующие действия:
        - `list`: Возвращает список всех пользователей. Доступно для аутентифицированных пользователей.
        - `retrieve`: Возвращает детали конкретного пользователя. Доступно для аутентифицированных пользователей.
        - `create`: Создает нового пользователя. Доступно только для администраторов.
        - `update`: Обновляет данные пользователя. Доступно только для администраторов.
        - `partial_update`: Частично обновляет данные пользователя. Доступно только для администраторов.
        - `destroy`: Удаляет пользователя. Доступно только для администраторов.

        Поля, возвращаемые в API:
        - `id`: Уникальный идентификатор пользователя.
        - `username`: Имя пользователя.
        - `email`: Электронная почта пользователя.
        - `is_staff`: Флаг, указывающий, является ли пользователь администратором.

        Права доступа:
        - Для просмотра списка пользователей или деталей пользователя требуется аутентификация.
        - Для создания, обновления и удаления пользователей требуется права администратора.
        """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Настройка прав доступа
    def get_permissions(self):
        """
        Настраивает права доступа в зависимости от действия.

        Returns:
            list: Список классов разрешений, которые будут применены к текущему действию.
        """
        if self.action == 'list' or self.action == 'retrieve':
            # Для просмотра списка пользователей или деталей.
            permission_classes = [IsAuthenticated]
        else:
            # Для создания, обновления и удаления пользователей
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]