# Restaurant menu

В проекте применен следующий стек технологий:
- FastAPI
- Uvicorn
- PosgresSQL
- SQLAlchemy
- Docker, docker-compose


## Задание
Написать проект на FastAPI с использованием PostgreSQL в качестве БД. В проекте следует реализовать REST API по работе с меню ресторана, все CRUD операции.
Даны 3 сущности: Меню, Подменю, Блюдо.

##### Зависимости:
- У меню есть подменю, которые к ней привязаны.
- У подменю есть блюда.

##### Условия:
- Блюдо не может быть привязано напрямую к меню, минуя подменю.
- Блюдо не может находиться в 2-х подменю одновременно.
- Подменю не может находиться в 2-х меню одновременно.
- Если удалить меню, должны удалиться все подменю и блюда этого меню.
- Если удалить подменю, должны удалиться все блюда этого подменю.
- Цены блюд выводить с округлением до 2 знаков после запятой.
- Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
- Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.
- Во время запуска тестового сценария БД должна быть пуста.

##### Start

1. Склонировать репозиторий

```python
git clone https://github.com/radik121/fastapi_menu.git
```

2. Перейти в деркторию с проектом

```python
cd fastapi_menu
```

3. Переименовать файл .env_dev на .env (тестовые переменные окружения)

```
mv .env_dev .env
```

4. Запустить web-приложение в контейнере Docker

```python
docker-compose up -d
```

5. Запустить тесты для api-запросов

```python
docker-compose -f docker-compose.test.yml up
```
