#!/bin/bash
# Docker entrypoint скрипт для запуска всех сервисов

set -e

echo "🐳 Docker Entrypoint"
echo "===================="

# Ждём базу данных
if [ -n "$DB_HOST" ]; then
    echo "⏳ Ожидание PostgreSQL ($DB_HOST:${DB_PORT:-5432})..."
    while ! pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -q; do
        sleep 1
    done
    echo "✅ PostgreSQL доступен"
fi

# Применяем миграции
echo "📦 Применение миграций..."
python manage.py migrate --noinput

# Собираем статику (для production)
if [ "$DJANGO_ENV" = "production" ]; then
    echo "📁 Сбор статических файлов..."
    python manage.py collectstatic --noinput
fi

# Запускаем микросервисы в фоне
echo "🚀 Запуск микросервиса Assistants (порт 7999)..."
python ./service/assistants/main.py &
ASSISTANTS_PID=$!

echo "🚀 Запуск микросервиса Sheets (порт 7998)..."
python -m service.sheets.main &
SHEETS_PID=$!

# Даём время на инициализацию
sleep 2

# Функция для корректного завершения
cleanup() {
    echo ""
    echo "⚠️  Завершение сервисов..."
    kill $ASSISTANTS_PID 2>/dev/null || true
    kill $SHEETS_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT

# Запускаем Django/Gunicorn
echo ""
echo "🌐 Запуск Django..."
echo "===================="

if [ "$DJANGO_ENV" = "production" ]; then
    # Production: Gunicorn
    exec gunicorn \
        --bind 0.0.0.0:${DJANGO_PORT:-8000} \
        --workers ${GUNICORN_WORKERS:-4} \
        --threads ${GUNICORN_THREADS:-2} \
        --access-logfile - \
        --error-logfile - \
        core.wsgi:application
else
    # Development: Django runserver
    exec python manage.py runserver 0.0.0.0:${DJANGO_PORT:-8000}
fi

