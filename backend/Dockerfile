FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt /app 

RUN pip3 install -r requirements.txt --no-cache-dir


COPY . .
RUN DJANGO_SUPERUSER_PASSWORD=administator python manage.py createsuperuser --noinput administator

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]