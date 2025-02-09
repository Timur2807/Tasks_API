from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Tasks
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth.models import User


User  = get_user_model()


class TaskAPITests(APITestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpass')

        # Создаем тестовую задачу
        self.task = Tasks.objects.create(
            title='Test Task',
            description='Task Description',
            user=self.user
        )

    # def test_user_registration(self):
    #     """
    #     Тест регистрации нового пользователя.
    #     """
    #     url = reverse('user-registration')
    #     data = {
    #         'username': 'newuser',
    #         'password': 'newpassword'
    #     }
    #     response = self.client.post(url, data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(User.objects.count(), 2)
    #     self.assertEqual(User.objects.get(username='newuser').username, 'newuser')

    def test_create_task(self):
        """
        Тест создания новой задачи.
        """
        url = reverse('task_api:tasks-list')
        data = {
            'title': 'New Task',
            'description': 'New Task Description',
            'due_date': '2023-12-31'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tasks.objects.count(), 2)
        self.assertEqual(Tasks.objects.get(id=2).title, 'New Task')

    def test_list_tasks(self):
        """
        Тест получения списка задач.
        """
        url = reverse('task_api:tasks-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.task.title)

    def test_retrieve_task(self):
        """
        Тест получения деталей задачи.
        """
        url = reverse('task_api:tasks-detail', args=[self.task.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.task.title)

    def test_update_task(self):
        """
        Тест обновления задачи.
        """
        url = reverse('task_api:tasks-detail', args=[self.task.id])
        data = {
            'title': 'Updated Task',
            'description': 'Updated Description',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')

    def test_partial_update_task(self):
        """
        Тест частичного обновления задачи.
        """
        url = reverse('task_api:tasks-detail', args=[self.task.id])
        data = {
            'description': 'Partially Updated Description',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, 'Partially Updated Description')

    def test_destroy_task(self):
        """
        Тест удаления задачи.
        """
        url = reverse('task_api:tasks-detail', args=[self.task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tasks.objects.count(), 0)

    def test_update_task_not_owner(self):
        """
        Тест попытки обновления задачи, созданной другим пользователем.
        """
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        task = Tasks.objects.create(
            title='Other User Task',
            description='Task Description',
            user=other_user
        )
        url = reverse('task_api:tasks-detail', args=[task.id])
        data = {
            'title': 'Attempted Update',
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy_task_not_owner(self):
        """
        Тест попытки удаления задачи, созданной другим пользователем.
        """
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        task = Tasks.objects.create(
            title='Other User Task',
            description='Task Description',
            user=other_user
        )
        url = reverse('task_api:tasks-detail', args=[task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


