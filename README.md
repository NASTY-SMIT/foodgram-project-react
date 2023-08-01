# Foodgram
## _Продуктовый помощник_
На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Сервисы и страницы проекта

- Главная страница
Содержимое главной страницы — список первых шести рецептов, отсортированных по дате публикации (от новых к старым). 
- Страница рецепта
На странице — полное описание рецепта. Для авторизованных пользователей — возможность добавить рецепт в избранное и в список покупок, возможность подписаться на автора рецепта.
- Страница пользователя
На странице — имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.
- Подписка на авторов
Подписка на публикации доступна только авторизованному пользователю. Страница подписок доступна только владельцу.
- Список избранного
Работа со списком избранного доступна только авторизованному пользователю. Список избранного может просматривать только его владелец.
- Список покупок
Работа со списком покупок доступна авторизованным пользователям. Список покупок может просматривать только его владелец. 
(Пользователь переходит на страницу Список покупок, там доступны все добавленные в список рецепты. Пользователь нажимает кнопку Скачать список и получает файл с суммированным перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».)

## Технологии
- Python 3.10
- Django 3.2
- Django REST framework 3.14
- Docker

## Как развернуть проект

Клонировать репозиторий и перейти в него в командной строке:

```sh
git clone https://github.com/yandex-praktikum/kittygram_backend.git 

cd kittygram_backend 

```

Cоздать и активировать виртуальное окружение:

```sh
python3 -m venv env 
```
- Если у вас Linux/macOS
```sh
source env/bin/activate 
```
- Если у вас windows
```sh
source env/scripts/activate 
```
Обновить pip
```sh
python3 -m pip install --upgrade pip 
```
Установить зависимости из файла requirements.txt:
```sh
pip install -r requirements.txt 
```
Выполнить миграции:
```sh
python3 manage.py migrate 
```
Запустить проект:
```sh
python3 manage.py runserver 
```

## Для заполнения файла переменных окружения .env вам понадобится следовать следующим шагам:
- Создайте файл с названием .env в корневой папке вашего проекта.
- Откройте файл .env в текстовом редакторе.
- Добавьте переменные окружения в формате KEY=VALUE. Каждая переменная должна быть указана на отдельной строке. Например:
```sh
   POSTGRES_DB=mydatabase
   POSTGRES_USER=myuser
   POSTGRES_PASSWORD=mypassword
   DB_NAME=mydatabase
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=mysecretkey
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   TIME_ZONE=Europe/Moscow
   USE_TZ=True
```
(Замените mydatabase, myuser, mypassword, localhost, 5432, mysecretkey, True, localhost,127.0.0.1, Europe/Moscow и True на соответствующие значения для вашего окружения.)
- Сохраните файл .env.

**By Shmidt Anastasia**
