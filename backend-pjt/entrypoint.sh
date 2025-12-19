#!/bin/sh

echo "⏳ Waiting for database..."

until python manage.py dbshell >/dev/null 2>&1; do
  sleep 1
done

echo "🚀 Running migrations..."
python manage.py migrate --noinput

echo "🎉 Starting Django server..."
exec "$@"
