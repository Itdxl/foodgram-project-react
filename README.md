# Дипломный проект YP
## Сайт: http://158.160.21.94/recipes
## Данные для входа администратора: 
логин: super@super.super 

пароль: super

## Данные для входа обычного пользователя: 
логин: testuser1@test1.test1

пароль: sometestpass

## Запуск проекта на своем устройстве:

Разверние проект:

```
git clone git@github.com:Itdxl/foodgram-project-react.git
```

```
python3 -m venv env
```

```
source venv/scripts/activate
```


```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

В директории backend:

Создайте env:
```
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=False
```

Создайте образ:

```
docker build -t itdxl/foodgramback:latest
```

В директории infra:

```
cd ../infra
```

```
docker-compose up
```


```
docker-compose exec -T backend python manage.py migrate
```


```
docker-compose exec -T backend python manage.py collectstatic --no-input
```


Откройте в бразуере:
```
localhost
```
