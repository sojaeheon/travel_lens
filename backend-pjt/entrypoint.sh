#!/bin/sh

echo "⏳ Waiting for database..."

until python manage.py dbshell >/dev/null 2>&1; do
  sleep 1
done

echo "🚀 Running migrations..."
python manage.py migrate --noinput

echo "🌍 Loading travel seed data..."
python manage.py load_travel_seed

echo "📰 Loading content seed..."
python manage.py load_content_seed


echo "🎉 Starting Django server..."
exec "$@"
