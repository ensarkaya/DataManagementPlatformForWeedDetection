#!/bin/bash

# Predefined variables from Django settings.py
your_database_name="mydatabase"
your_username="myuser"
your_password="123456789"

# Check if user already exists and create if not
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (
            SELECT FROM pg_catalog.pg_roles 
            WHERE  rolname = '$your_username') THEN

            CREATE ROLE $your_username LOGIN PASSWORD '$your_password';
        END IF;
    END
    \$\$;

    -- Check if database already exists and create if not
    SELECT 'CREATE DATABASE $your_database_name'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$your_database_name')\gexec

    -- Grant privileges
    GRANT ALL PRIVILEGES ON DATABASE $your_database_name TO $your_username;
EOSQL

# Access PostgreSQL prompt for further configuration
psql -v ON_ERROR_STOP=1 --username "$your_username" --dbname "$your_database_name" <<-EOSQL
    -- Install the PostGIS extension
    CREATE EXTENSION IF NOT EXISTS postgis;

    -- Check if the extension was successfully installed
    SELECT PostGIS_full_version();
EOSQL

echo "PostgreSQL and PostGIS setup completed."
