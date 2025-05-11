# Documentação de Deploy para Aplicação Django com Coolify

## 1. Visão Geral

Este documento detalha os passos e configurações necessárias para realizar o deploy da aplicação Django "igmembros-manus" utilizando Coolify com Docker. O processo envolve a configuração do ambiente, a criação de arquivos Docker e a definição de variáveis de ambiente para uma implantação bem-sucedida.

## 2. Arquivos Gerados

Os seguintes arquivos foram criados e adicionados à raiz do projeto (`/home/ubuntu/igmembros-manus/`):

*   `Dockerfile`: Define a imagem Docker para a aplicação Django.
*   `.dockerignore`: Especifica arquivos e diretórios a serem ignorados durante o build da imagem Docker.
*   `docker-compose.yml`: Um arquivo básico para desenvolvimento local e referência. Para produção no Coolify, você geralmente configurará os serviços diretamente na interface do Coolify, mas este arquivo pode guiar a configuração de variáveis de ambiente e portas.
*   `entrypoint.sh`: Script executado ao iniciar o contêiner para aplicar migrações, coletar arquivos estáticos e iniciar o Gunicorn.
*   `requirements.txt`: (Assumindo que já existe e está atualizado com todas as dependências, incluindo `gunicorn` e `psycopg2-binary` se estiver usando PostgreSQL).

## 3. Conteúdo dos Arquivos de Deploy

### 3.1. Dockerfile

```dockerfile
# Use uma imagem Python oficial como imagem pai
FROM python:3.11-slim-bullseye

# Define variáveis de ambiente para evitar a criação de arquivos .pyc e para buffer de saída
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Instala dependências do sistema (descomente e ajuste se necessário)
# Exemplo para PostgreSQL e Pillow:
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libpq-dev libjpeg-dev zlib1g-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt /app/

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o script de entrypoint
COPY ./entrypoint.sh /app/entrypoint.sh
# Garante que o script seja executável
RUN chmod +x /app/entrypoint.sh

# Copia o restante do código do projeto para o diretório de trabalho
COPY . /app/

# Expõe a porta em que o Gunicorn será executado (Coolify pode sobrescrever isso)
EXPOSE 8000

# Define o entrypoint que executará as migrações, coletará estáticos e iniciará o Gunicorn
ENTRYPOINT ["/app/entrypoint.sh"]
```

### 3.2. .dockerignore

```
# Arquivos e diretórios do Git
.git
.gitignore

# Arquivos de ambiente virtual
venv/
.venv/
env/

# Arquivos de cache do Python
__pycache__/
*.pyc
*.pyo

# Arquivos de configuração local
.env

# Banco de dados SQLite (se usado apenas para desenvolvimento)
db.sqlite3
*.sqlite3

# Arquivos de mídia (geralmente servidos por um serviço externo em produção)
media/

# Arquivos de teste e cobertura
tests/
.coverage
htmlcov/

# Documentação (se não for parte do build da aplicação)
docs/

# Arquivos de IDE/editor
.idea/
.vscode/
*.sublime-project
*.sublime-workspace

# Arquivos de sistema operacional
.DS_Store
Thumbs.db

# Logs
*.log

# Arquivos de build/distribuição Python não necessários na imagem final
build/
dist/
*.egg-info/

# Arquivos de backup
*.bak
*~

# Arquivos de cache de linters/formatters
.mypy_cache/
.pytest_cache/

# Node modules (se o frontend for buildado separadamente)
node_modules/
```

### 3.3. docker-compose.yml (para desenvolvimento/referência)

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    command: python manage.py runserver 0.0.0.0:8000 # Para desenvolvimento. Em produção, o entrypoint.sh usará Gunicorn.
    volumes:
      - .:/app # Mapeia o código local para dentro do contêiner para hot-reloading
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=django-insecure-coolify-dev-secret-key # TROCAR EM PRODUÇÃO
      - DEBUG=1 # 1 para desenvolvimento, 0 para produção
      # Configurações de banco de dados (exemplo para SQLite em dev)
      - DB_ENGINE=django.db.backends.sqlite3
      - DB_NAME=/app/db.sqlite3 # Caminho dentro do contêiner
      # Para PostgreSQL (exemplo):
      # - DB_ENGINE=django.db.backends.postgresql
      # - DB_NAME=your_db_name
      # - DB_USER=your_db_user
      # - DB_PASSWORD=your_db_password
      # - DB_HOST=db # Nome do serviço do banco de dados no docker-compose
      # - DB_PORT=5432
    depends_on:
      - db # Descomente se estiver usando um serviço de banco de dados no compose

# Descomente e configure se precisar de um banco de dados para desenvolvimento local
#  db:
#    image: postgres:15-alpine
#    volumes:
#      - postgres_data:/var/lib/postgresql/data/
#    environment:
#      - POSTGRES_DB=your_db_name
#      - POSTGRES_USER=your_db_user
#      - POSTGRES_PASSWORD=your_db_password
#    ports:
#      - "5432:5432"

#volumes:
#  postgres_data: # Persiste os dados do PostgreSQL
```

### 3.4. entrypoint.sh

```bash
#!/bin/sh

# Aplica as migrações do banco de dados
echo "Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
# A opção --clear remove os arquivos estáticos antigos antes de copiar os novos.
python manage.py collectstatic --noinput --clear

# Inicia o servidor Gunicorn
# O número de workers pode ser ajustado. Uma recomendação comum é (2 * NÚMERO_DE_CORES) + 1.
# Coolify pode injetar a variável $PORT, ou você pode fixar em 8000 se o EXPOSE no Dockerfile for 8000.
echo "Iniciando Gunicorn na porta ${PORT:-8000}..."
exec gunicorn templo_digital_django.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${GUNICORN_WORKERS:-3}
```

## 4. Checklist de Variáveis de Ambiente para Produção no Coolify

Configure estas variáveis na interface do Coolify para sua aplicação:

*   `SECRET_KEY`: **OBRIGATÓRIO**. Uma string longa, aleatória e secreta. Não use a de desenvolvimento.
*   `DEBUG`: **OBRIGATÓRIO**. Defina como `0` (ou `False`) em produção.
*   `ALLOWED_HOSTS`: **OBRIGATÓRIO**. Lista de hosts/domínios permitidos para sua aplicação (ex: `seudominio.com,www.seudominio.com`). Coolify geralmente provê um domínio, adicione-o aqui.
*   `DATABASE_URL`: **OBRIGATÓRIO (se usando banco de dados externo)**. URL de conexão completa para seu banco de dados PostgreSQL no formato `postgres://USER:PASSWORD@HOST:PORT/NAME`. Se estiver usando o serviço de PostgreSQL do Coolify, ele fornecerá essa URL.
    *   Ou, individualmente (se `DATABASE_URL` não for usado diretamente pelo Django settings):
        *   `DB_ENGINE`: `django.db.backends.postgresql`
        *   `DB_NAME`: Nome do seu banco de dados.
        *   `DB_USER`: Usuário do banco de dados.
        *   `DB_PASSWORD`: Senha do banco de dados.
        *   `DB_HOST`: Host do banco de dados (fornecido pelo Coolify se usar o serviço deles).
        *   `DB_PORT`: Porta do banco de dados (geralmente `5432` para PostgreSQL).
*   `STATIC_ROOT`: Geralmente `/app/staticfiles` (ou o valor definido em `settings.py`). O `collectstatic` no `entrypoint.sh` usará isso.
*   `MEDIA_ROOT`: Caminho para onde os arquivos de mídia enviados pelos usuários são armazenados (ex: `/app/mediafiles`).
*   `MEDIA_URL`: URL base para servir arquivos de mídia (ex: `/media/`).
*   `STATIC_URL`: URL base para servir arquivos estáticos (ex: `/static/`).
*   `CSRF_TRUSTED_ORIGINS`: **IMPORTANTE**. Lista de origens confiáveis para CSRF, inclua o domínio da sua aplicação no Coolify (ex: `https://seudominio.coolify.app`).
*   `EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Se sua aplicação envia emails.
*   `GUNICORN_WORKERS`: (Opcional) Número de workers para o Gunicorn. Padrão no `entrypoint.sh` é 3. Pode ser ajustado conforme os recursos do seu plano no Coolify.
*   `PORT`: (Opcional) Coolify geralmente injeta a variável `$PORT`. O `entrypoint.sh` usa `${PORT:-8000}`.

## 5. Instruções de Deploy no Coolify

1.  **Prepare seu Repositório Git:**
    *   Adicione os arquivos `Dockerfile`, `.dockerignore`, `docker-compose.yml` (opcional, mais para dev local) e `entrypoint.sh` à raiz do seu projeto.
    *   Certifique-se de que `requirements.txt` está atualizado e inclui `gunicorn` e `psycopg2-binary` (ou o driver do seu banco de dados).
    *   Faça commit e push dessas alterações para o seu repositório Git (GitHub, GitLab, etc.).

2.  **No Coolify:**
    *   Crie um novo projeto ou use um existente.
    *   Adicione um novo recurso do tipo "Application".
    *   Conecte seu repositório Git.
    *   **Configuração do Build:**
        *   Selecione o branch correto.
        *   **Build Pack:** Escolha "Dockerfile".
        *   **Dockerfile Location:** Deixe como `/Dockerfile` (se estiver na raiz do projeto).
    *   **Port:** Defina a porta que você expôs no Dockerfile (ex: `8000`). Coolify mapeará isso para as portas 80/443 publicamente.
    *   **Variáveis de Ambiente:** Adicione todas as variáveis de ambiente listadas na Seção 4.
    *   **Configurações de Domínio:** Configure seu domínio personalizado ou use o domínio fornecido pelo Coolify.
    *   **Banco de Dados (se necessário):**
        *   Se você precisar de um banco de dados PostgreSQL, adicione um novo serviço "PostgreSQL" no Coolify.
        *   O Coolify fornecerá as credenciais e a URL de conexão (`DATABASE_URL`) que você usará nas variáveis de ambiente da sua aplicação Django.
    *   **Armazenamento Persistente (Persistent Storage):**
        *   Se sua aplicação precisa armazenar arquivos de mídia (`MEDIA_ROOT`) ou outros dados persistentes no sistema de arquivos do contêiner, configure um volume persistente no Coolify e mapeie-o para o caminho correspondente dentro do contêiner.

3.  **Deploy:**
    *   Clique no botão "Deploy".
    *   Acompanhe os logs de build e deploy no Coolify para verificar se há erros.
    *   O `entrypoint.sh` cuidará de executar `migrate` e `collectstatic` automaticamente.

4.  **Pós-Deploy:**
    *   Verifique se a aplicação está acessível no domínio configurado.
    *   Teste todas as funcionalidades, especialmente aquelas que dependem de banco de dados e envio de arquivos.
    *   Monitore os logs da aplicação no Coolify.

## 6. Considerações Importantes

*   **`settings.py`:** Certifique-se de que seu `settings.py` está configurado para ler as variáveis de ambiente (ex: usando `os.getenv()`).
*   **Arquivos Estáticos:** Para servir arquivos estáticos em produção com Django e Gunicorn, é comum usar o `whitenoise`. Certifique-se de que ele está configurado corretamente em seu `settings.py` e `wsgi.py` se você não estiver usando um serviço de CDN separado ou Nginx na frente.
    ```python
    # settings.py
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    # Adicione 'whitenoise.middleware.WhiteNoiseMiddleware' ao MIDDLEWARE após o SecurityMiddleware
    ```
*   **Segurança:** Nunca comite chaves secretas ou senhas no seu repositório Git. Use sempre variáveis de ambiente.

Este guia deve fornecer uma base sólida para implantar sua aplicação Django no Coolify. Ajuste as configurações conforme a necessidade específica do seu projeto.

