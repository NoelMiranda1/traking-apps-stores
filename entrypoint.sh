#!/bin/sh
set -e # Exit immediately if a command exits with a non-zero status.

# Wait for database to be ready
echo "Waiting for database..."
# Check if required env vars are set, provide defaults if not for safety
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-postgres}
DB_NAME=${POSTGRES_DB:-base}

while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -q; do
  echo "Database is unavailable - sleeping"
  sleep 2
done
echo "Database is ready!"

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Execute the command passed as arguments
exec "$@" 