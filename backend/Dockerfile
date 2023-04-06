FROM python:3.7-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Выполните миграции Django
RUN python manage.py migrate

# Cтатикa
# RUN python manage.py collectstatic --noinput

# EXPOSE 8000

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]