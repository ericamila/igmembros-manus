# Use uma imagem Python oficial como imagem pai
FROM python:3.13-slim-bullseye

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Instala dependências do sistema (se necessário, ex: para Pillow, psycopg2-binary)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libpq-dev libjpeg-dev zlib1g-dev \
#     && rm -rf /var/lib/apt/lists/*

# Instala pipenv (se o projeto usar Pipfile em vez de requirements.txt)
# RUN pip install pipenv

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt /app/

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o entrypoint script
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copia o restante do código do projeto para o diretório de trabalho
COPY . /app/

# Coleta arquivos estáticos (será feito no entrypoint para ter acesso às variáveis de ambiente se necessário)
# RUN python manage.py collectstatic --noinput

# Expõe a porta em que o Gunicorn será executado
EXPOSE 8000

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
