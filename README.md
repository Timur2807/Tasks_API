Tasks API
Tasks API
Описание проекта
Tasks API — это Django-приложение для управления задачами. Оно предоставляет RESTful API для создания, чтения, обновления и удаления задач. Каждая задача содержит следующие поля:

Название (title)

Описание (description)

Срок выполнения (due_date)

Пользователь (user), который создал задачу.

Проект использует:

Django — веб-фреймворк для создания приложения.

Django REST Framework (DRF) — для создания API.

PostgreSQL — база данных для хранения данных.

Redis — для кэширования данных.

Docker — для контейнеризации приложения, базы данных и Redis.



Инструкции по запуску
Требования
Установленный Docker и Docker Compose.

Установленный Python (если вы хотите запускать проект без Docker).
Запуск с помощью Docker
Клонируйте репозиторий:
https://github.com/Timur2807/Tasks_API.git
Переходим в директорию:
cd Tasks_API

Соберите и запустите контейнеры:
docker-compose up --build

Выполните миграции:
Откройте новое окно терминала и выполните:
docker-compose exec web python manage.py migrate

Создайте суперпользователя (опционально):
docker-compose exec web python manage.py createsuperuser

Доступ к приложению:
После запуска приложение будет доступно по адресу:
http://localhost:8000
или
http://127.0.0.1:8000/

Запуск без Docker
Создайте вертуальное окружение в рабочей директории:
python -m venv venv

Активируйте виртуальное окружение:
venv\Scripts\activate- если через cmd
.\venv\Scripts\Activate.ps1 - через psh

Установите зависимости:
внимание для докера нужен postgresql бинарный
ознакомьтесь с списком разкоменьтарьте нужный 
pip install -r requirements.txt

Настройте базу данных:
Убедитесь, что у вас установлен и запущен PostgreSQL. Затем создайте базу данных и пользователя:
CREATE DATABASE tasks_db;
CREATE USER timur WITH PASSWORD '123';
GRANT ALL PRIVILEGES ON DATABASE tasks_db TO timur;

Выполните миграции:
python manage.py migrate

Создайте суперпользователя (опционально):
python manage.py createsuperuser

Запустите сервер:
python manage.py runserver

Доступ к приложению:
После запуска приложение будет доступно по адресу:
http://localhost:8000/
или
http://127.0.0.1:8000/

Тестирование
Запуск тестов
С Docker:
docker-compose exec web python manage.py test

Без Docker:
Убедитесь, что у вас установлен pytest и pytest-django, затем выполните:
pytest
или 
python manage.py test

Примеры API-запросов
Создание задачи:
curl -X POST http://127.0.0.1:8000/api/tasks/ \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Новая задача",
           "description": "Описание задачи",
           "due_date": "2023-12-31T00:00:00Z"
         }'

Получение списка задач:
curl -X GET http://localhost:8000/api/tasks/
или
curl -X GET http://127.0.0.1:8000/api/tasks/

Обновление задачи:
curl -X PUT http://127.0.0.1:8000/api/tasks/1/ \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Обновленная задача",
           "description": "Обновленное описание",
           "due_date": "2023-12-31T00:00:00Z"
         }'

Удаление задачи:
curl -X DELETE http://localhost:8000/api/tasks/1/
curl -X DELETE http://127.0.0.1:8000/api/tasks/1/


Структура проекта:
tasks-api/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── manage.py
├── Tasks/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── task_api/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── views.py
│   └── urls.py
└── README.md