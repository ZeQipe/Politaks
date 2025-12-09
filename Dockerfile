FROM debian:12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем Python и зависимости
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/bin/python3 /usr/bin/python

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Копируем проект
COPY . .

# Делаем entrypoint исполняемым
RUN chmod +x docker-entrypoint.sh

# Создаем директории для статики, медиа и логов
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    /app/service/assistants/data/logs \
    /app/service/sheets/data/logs

# Создаем пользователя для запуска приложения
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

# Открываем порты: Django (8000), Assistants (7999), Sheets (7998)
EXPOSE 8000 7999 7998

# Переменные окружения по умолчанию
ENV DJANGO_ENV=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DOCKER_CONTAINER=1

# Entrypoint для запуска всех сервисов
ENTRYPOINT ["./docker-entrypoint.sh"]
