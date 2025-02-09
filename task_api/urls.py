from django.urls import path,include
from .views import UserRegistrationView
from rest_framework.routers import DefaultRouter
from task_api.views import TaskViewSet, UserViewSet

app_name = 'task_api'
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('tasks/', include(router.urls)),
    path('users/', include(router.urls)),
]