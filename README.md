# 1. Создать виртуальное окружение
python -m venv venv
# 2. Активировать его
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
# 3. Установить Django
pip install Django
# 4. Применить миграции
python manage.py migrate
# 5. Запустить сервер
python manage.py runserver
