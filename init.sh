#!/bin/sh
set -e

# Directly execute SQL commands with environment variable substitution
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE weather_data (
        id SERIAL PRIMARY KEY,
        dt BIGINT,
        city_id INT,
        cod INT,
        base TEXT,
        name TEXT,
        sys_id INT,
        sys_type INT,
        timezone INT,
        wind_deg INT,
        coord_lat FLOAT,
        coord_lon FLOAT,
        main_temp FLOAT,
        timestamp TIMESTAMP,
        clouds_all INT,
        sys_sunset BIGINT,
        visibility INT,
        wind_speed FLOAT,
        sys_country TEXT,
        sys_sunrise BIGINT,
        weather_id INT,
        main_humidity INT,
        main_pressure INT,
        main_temp_max FLOAT,
        main_temp_min FLOAT,
        weather_icon TEXT,
        weather_main TEXT,
        main_feels_like FLOAT,
        weather_description TEXT
    );

    CREATE USER $POSTGRES_CUSTOM_USER WITH PASSWORD '$POSTGRES_CUSTOM_PASSWORD';

    GRANT ALL PRIVILEGES ON TABLE weather_data TO $POSTGRES_CUSTOM_USER;
    GRANT ALL PRIVILEGES ON SEQUENCE weather_data_id_seq TO $POSTGRES_CUSTOM_USER;
EOSQL
