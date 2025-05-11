#!/bin/sh

# Aplica as migrações do banco de dados
echo "Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Inicia o servidor Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn templo_digital_django.wsgi:application --bind 0.0.0.0:8000 --workers 3

