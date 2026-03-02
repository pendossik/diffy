# settings_dev.py
from .settings import *
import os

# Переопределяем базу данных, чтобы не ломать основную
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # База будет называться db_dev.sqlite3
        'NAME': BASE_DIR / 'db_dev.sqlite3', 
    }
}

DEBUG = True