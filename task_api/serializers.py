from rest_framework import serializers
from django.contrib.auth.models import User

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from .models import Tasks

User = get_user_model()

class UserRegistrationSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)  # Пароль не возвращается и должен быть не менее 8 символов

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'email': {'required': True},  # Делаем email обязательным полем
        }

    def validate_password(self, value):
        # Пример простой валидации пароля
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов.")
        return value

    def create(self, validated_data):
        # Создаем пользователя с хэшированным паролем, используя распаковку словаря
        user = User.objects.create_user(**validated_data)
        return user


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Tasks
        fields = ('id', 'title', 'description', 'due_date', 'user')
        read_only_fields = ('id', 'user')  # Поле 'user' будет автоматически заполняться

    def create(self, validated_data):
        # Автоматически привязываем задачу к текущему пользователю
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff')  # Поля, которые будут возвращаться