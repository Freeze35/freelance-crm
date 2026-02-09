FROM python:3.11-slim

# System dependencies for WeasyPrint and Supervisor
RUN apt-get update && apt-get install -y \
libpango-1.0-0 \
libpangocairo-1.0-0 \
libgdk-pixbuf-2.0-0 \
libffi-dev \
libjpeg-dev \
libwebp-dev \
supervisor \
&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a user (required for HF)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

EXPOSE 7860

# Run via supervisor (don't forget to create supervisord.conf in the root directory!)
CMD ["supervisord", "-c", "supervisord.conf"]