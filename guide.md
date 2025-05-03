




### instalar biblioteca de gráficos e frontend

Para que o Tailwind funcione na Vercel, você precisa adicionar um passo de build de frontend ao seu processo de implantação. Isso geralmente envolve:
- 1 Inicializar Node.js: Na raiz do seu projeto, execute ````npm init -y```` para criar um package.json.
- 2  Instalar Dependências: Instale o Tailwind e suas dependências: npm install -D tailwindcss postcss autoprefixer @tailwindcss/forms (ou use pnpm install -D ...).
- 3 Configurar Tailwind: Crie e configure os arquivos tailwind.config.js e postcss.config.js na raiz do projeto. O tailwind.config.js deve ser configurado para escanear seus templates Django (**/*.html) e especificar o arquivo CSS de saída (ex: ./theme/static/css/dist/styles.css).
- 4 Adicionar Script de Build: No package.json, adicione um script para construir o CSS, por exemplo:
````json
"scripts": {
  "build:css": "tailwindcss -i ./theme/static_src/src/input.css -o ./theme/static/css/dist/styles.css --minify"
}
````
- 5 Atualizar vercel.json (ou Configurações Vercel): Modifique sua configuração de implantação na Vercel para:
* Detectar a presença do package.json.
* Executar npm install (ou pnpm install).
* Executar o script de build do CSS (npm run build:css ou pnpm build:css) antes do python manage.py collectstatic ser executado pelo buildpack do Python.

Como alternativa mais simples, você pode gerar o arquivo CSS (styles.css) localmente usando o comando do Tailwind e commitar esse arquivo CSS gerado diretamente no seu repositório Git. O collectstatic então o incluirá no build. No entanto, a abordagem padrão é construir o CSS durante a implantação.
Com essa configuração, a Vercel irá gerar o CSS necessário antes de servir sua aplicação Django.

### separar banco de dados desenvolvimento e produção
Por padrão, usaremos SQLite, e para produção (como na Vercel ou no ambiente Supabase):
ajustar o settings.py

pip install dj-database-url
echo "dj-database-url" >> requirements.txt
