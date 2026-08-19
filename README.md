# Сервис управления рассылками

Веб-приложение на Django для управления email-рассылками.

## Функциональность

- Управление клиентами (CRUD)
- Управление сообщениями (CRUD)
- Управление рассылками (CRUD)
- Отправка писем по требованию
- Логирование попыток отправки
- Статистика на главной странице
- Регистрация и аутентификация пользователей
- Разграничение прав доступа (пользователь / менеджер)
- Кеширование через Redis

---

## Установка и запуск

### 1. Клонировать репозиторий

git clone https://github.com/ваш_логин/coursework_django.git
cd coursework_django

### 2. Создать виртуальное окружение

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

### 3. Установить зависимости

pip install -r requirements.txt

### 4. Настроить базу данных PostgreSQL
Создайте базу данных coursework_db и настройте .env:


NAME=coursework_db
USER=postgres
PASSWORD=ваш_пароль
HOST=localhost
PORT=5432

### 5. Применить миграции

python manage.py migrate

### 6. Создать суперпользователя

python manage.py createsuperuser

### 7. Запустить сервер

python manage.py runserver


## Использование


Главная страница: http://127.0.0.1:8000/

Админка: http://127.0.0.1:8000/admin

Регистрация: /users/register/

Вход: /users/login/