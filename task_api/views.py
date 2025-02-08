from django.shortcuts import render

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


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Разрешить регистрацию всем

    def post(self, request, *args, **kwargs):
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
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Автоматически привязывает задачу к текущему пользователю при создании.

        Args:
            serializer: Сериализатор для создания задачи.
        """
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Обновляет задачу. Доступно только для владельца задачи.

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

        # Вызываем родительский метод для обновления
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Частично обновляет задачу. Доступно только для владельца задачи.

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

        # Вызываем родительский метод для частичного обновления
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет задачу. Доступно только для владельца задачи.

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