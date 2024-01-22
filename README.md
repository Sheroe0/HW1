# Запуск проекта

## 1. Склонируйте репозиторий
```
git clone https://github.com/gmohmad/Y_lab_FastAPI.git
```
## 2. Подготовьте базу данных (PostgreSQL)
```
создайте пользователя
создайте базу данных
```
## 3. Настроить проект
```
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