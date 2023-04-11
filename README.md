# Дипломный проект YP
## Сайт: http://158.160.21.94/recipes
## Данные для входа администратора: 
логин: super@super.super 

пароль: super

## Данные для входа обычного пользователя: 
логин: testuser1@test1.test1

пароль: sometestpass

### Запуск проекта на своем устройстве:

Скопируйте проект на свой компьютер:

```
git clone https://github.com/LariosDeen/foodgram-project-react
```

```
python3 -m venv env
```

```
source env/bin/activate
```


```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Перейдите в директорию проекта:

```
cd backend
```

Создайте файл .env в директории backend и заполните его данными по этому 
образцу:

```
SECRET_KEY='django-insecure-nsxoy+s&z^f(2$vot&-m!3+uacrm1jikv6!mb+ut&*thlrn=m7'
DB_ENGINE=django.db.backends.postgresql
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=False
```

Создайте образ backend (текущая директория должна быть backend):

```
docker build -t dimlar/foodgram_backend:latest .
```

Перейдите в директорию infra:

```
cd ../infra
```

Запустите docker-compose:

```
docker-compose up
```

Выполните миграции в контейнере созданном из образа backend:

```
docker-compose exec -T backend python manage.py migrate
```

Загрузите статические файлы в контейнере созданном из образа backend:

```
docker-compose exec -T backend python manage.py collectstatic --no-input
```

Запустите проект в браузере.
Введите в адресную строку браузера:

```
localhost
```
