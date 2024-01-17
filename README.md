## Проект доступен по ссылкам:

```
- https://foodxgram.bounceme.net
- https://foodxgram.bounceme.net/admin/
- username: lord
- email: lord@gmail.com
- password: lord
```

# Foodgram - социальная сеть для размещение фотографий домашних животных.

## Описание проекта
Foodgram - сайт, на котором пользователи публикуют свои рецепты, добавляют другие рецепты в избранное и подписываются на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

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

Создать файл .evn для хранения ключей:

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
docker compose -f docker-compose.production.yml up
```

Выполнить миграции, сбор статики:

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/

```

Создать суперпользователя:

```
docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

После запуска проекта документация доступна по адресу:

```
http://localhost/api/docs/
```
![1d004fa6-1350-404b-a4fc-8758f9e301d0](https://github.com/lordrie/foodgram-project-react/assets/131662299/ee358f66-ec71-47a9-83ea-d10becf30b8c)

