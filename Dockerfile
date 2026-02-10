FROM python:3.11-slim

# Системные зависимости для WeasyPrint и Redis-клиента
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    redis-server \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Даем права на выполнение скрипту запуска
RUN chmod +x start.sh

# Открываем порт для Django
EXPOSE 8000

CMD ["./start.sh"]