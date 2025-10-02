# diffy

для запуска необходимо:
Создать окружение
python -m venv .venv

Активировать окружение
.venv\Scripts\activate

Установить зависимости из requirements.txt
pip install -r requirements.txt

Сделать миграции для создания таблиц в бд (у вас будут пустые таблицы, напишу тесты позже для добавления элементов)
python manage.py makemigrations
python manage.py migrate

запустить, перейдя в папку с django-проектом
cd diffy_project
python manage.py runserver