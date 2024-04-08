#!/bin/bash
set -e

echo "PostgreSQL started, initializing database..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE $DB_NAME;
	ALTER USER "$POSTGRES_USER" WITH PASSWORD '$POSTGRES_PASSWORD';
    ALTER ROLE $POSTGRES_USER SET client_encoding TO 'utf8';
    ALTER ROLE $POSTGRES_USER SET default_transaction_isolation TO 'read committed';
    ALTER ROLE $POSTGRES_USER SET timezone TO 'Asia/Seoul';
    GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $POSTGRES_USER;
    ALTER DATABASE $DB_NAME OWNER TO $POSTGRES_USER;
EOSQL

echo "Database initialized."
