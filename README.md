# Foodgram: Сайт с рецептами и списком покупок"

## Описание проекта

"Foodgram" - это веб-приложение, которое позволяет пользователям:

- Публиковать рецепты с фото, видео, описанием и списком ингредиентов.
- Просматривать рецепты других пользователей, сортировать их по дате, тегам, категории.
- Добавлять рецепты в избранное и создавать список покупок.
- Подписываться на других пользователей и следить за их обновлениями.
- Оставлять комментарии к рецептам.
- Редактировать свои рецепты и удалять их.

## Технологии
- Python 3.9
- Django==3.2.3
- djangorestframework==3.12.4
- gunicorn==20.1.0
- Docker
- Nginx

## Автор
[@lordrie](https://github.com/lordrie)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:lordrie/foodgram-project-react.git
```

Перейти в директорию
```
cd foodgram-project-react/infra
```

Создать файл .evn для хранения ключей в папке:

```
SECRET_KEY=''
DEBUG = 
ALLOWED_HOSTS=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DB_HOST=
DB_PORT=
```

Запустить docker-compose.production:

```
docker compose up --build 
```

Выполнить миграции, сбор статики, создание суперпользователя:

```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
docker compose exec backend python manage.py createsuperuser
```

После запуска проекта документация доступна по адресу:

```
http://localhost/
http://localhost/api/docs/
```
![1d004fa6-1350-404b-a4fc-8758f9e301d0](https://github.com/lordrie/foodgram-project-react/assets/131662299/ee358f66-ec71-47a9-83ea-d10becf30b8c)

