# Запуск проекта

## 1. Склонируйте репозиторий
```
git clone https://github.com/gmohmad/HW.git
```
## 2. Подготовьте базу данных (PostgreSQL)
```
создайте пользователя
создайте базу данных
```
## 3. Настроить проект
```
активируйте окружение
venv\Scripts\activate.bat - для Windows;
source venv/bin/activate - для Linux и MacOS.

установите зависимости pip install -r requirements.txt

зайдите в файл database.py
измените строку DATABASE_URL = "postgresql+asyncpg://postgres:123tyklty@localhost:5432/postgres" под вашу базу
должно получиться так: DATABASE_URL = "postgresql+asyncpg://USER:PASS@HOST:PORT/NAME"
раскоментируйте 21-23 строку и запустите database.py
закоментируйте или удалите строки 21-23
```
## 4. Запустите сервер
```
uvicorn src.main:app --reload
```
