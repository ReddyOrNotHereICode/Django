#!/bin/sh

# Wait for the database to be ready
TIMEOUT=60
COUNT=0
until nc -z db 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 1
  COUNT=$((COUNT + 1))
  if [ $COUNT -ge $TIMEOUT ]; then
    echo "Timeout waiting for PostgreSQL"
    exit 1
  fi
done

# Make and run migrations
echo "Making migrations..."
python manage.py makemigrations --noinput
echo "Applying migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring superuser exists..."
  python manage.py shell << 'EOF'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if username and email and password:
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
EOF
fi

# Seed the database with base data if only superuser exists
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  USER_COUNT=$(python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())")
  if [ "$USER_COUNT" -eq 1 ]; then
    echo "Seeding database with base data..."
    python manage.py shell < /app/seed_data.py
  fi
fi

# Start the server
exec "$@"
