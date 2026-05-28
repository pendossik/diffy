# diffy

Для запуска проекта нужно скачать папку бэкенда и фронтенда. В корне всего прокта необходимо создать файл docker-compose.yml
с таким содержимым:
```
version: '3.8'

services:
  db:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_DB: diffy_db
      POSTGRES_USER: diffy_user
      POSTGRES_PASSWORD: diffy_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./diffy
    ports:
      - "8000:8000"
    volumes:
      - ./diffy:/app
    env_file:
      - ./diffy/diffy_project/.env
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true

volumes:
  postgres_data:
```
Для запуска всего проекта
```docker-compose up --build```

------------------

Для запуска только бэкенда локально:
Создать окружение
```python -m venv .venv```

Активировать окружение
```.venv\Scripts\activate```

Установить зависимости из requirements.txt
```pip install -r requirements.txt```

Сделать миграции для создания таблиц в бд (у вас будут пустые таблицы, напишу тесты позже для добавления элементов)
```
python manage.py makemigrations
python manage.py migrate
```

запустить, перейдя в папку с django-проектом
```
cd diffy_project
python manage.py runserver
```
