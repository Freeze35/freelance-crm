FROM python:3.11-slim

# System dependencies + git and git-lfs
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

# If Koyeb passes a .git folder, we pull the actual files instead of pointers.
# If there is no .git folder, the command will simply be skipped.
RUN if [ -d ".git" ]; then git lfs pull; fi

# Grant execution rights to the launch script
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]