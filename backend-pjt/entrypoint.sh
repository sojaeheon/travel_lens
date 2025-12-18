#!/bin/sh

echo "⏳ Waiting for database..."

# Django가 DB 연결 가능해질 때까지 대기
until python manage.py migrate --check >/dev/null 2>&1; do
  sleep 1
done

echo "🚀 Running migrations..."
python manage.py migrate --noinput

echo "🎉 Starting Django server..."
exec "$@"
