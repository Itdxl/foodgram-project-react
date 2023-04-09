FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt /app 

RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('administator', 'admin@example.com', 'administator')" | python manage.py shell

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]