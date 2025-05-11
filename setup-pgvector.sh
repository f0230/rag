#!/bin/bash
# Script to fix pgvector installation issues

# Install PostgreSQL client tools
apt-get update
apt-get install -y --no-install-recommends postgresql-client

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to start..."
until pg_isready -h postgres -U postgres; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Create the extension
echo "Creating pgvector extension..."
PGPASSWORD=postgres psql -h postgres -U postgres -d khoj -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "pgvector extension setup complete!"