FROM python:3.11-slim

# Системные зависимости + git и git-lfs
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    redis-server \
    git \
    git-lfs \
    && git lfs install \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Если Koyeb передает папку .git, то вытягиваем реальные файлы вместо указателей
# Если папки .git нет, команда просто пропустится
RUN if [ -d ".git" ]; then git lfs pull; fi

# Даем права на выполнение скрипту запуска
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]