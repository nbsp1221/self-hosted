#!/bin/bash

set -e

SQL_COMMANDS="
  CREATE USER ${N8N_POSTGRES_USER} WITH PASSWORD '${N8N_POSTGRES_PASSWORD}';
  GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${N8N_POSTGRES_USER};
  GRANT CREATE ON SCHEMA public TO ${N8N_POSTGRES_USER};
"

if [ -n "${N8N_POSTGRES_USER:-}" ] && [ -n "${N8N_POSTGRES_PASSWORD:-}" ]; then
  echo "$SQL_COMMANDS" | psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"
else
  echo "No Environment variables given!"
fi
