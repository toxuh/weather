import requests
import time
import os
import threading
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
import psycopg2
from psycopg2.extras import Json

app = FastAPI()

load_dotenv()

# Load environment variables
POSTGRES_HOST = "db"
POSTGRES_USER = os.getenv("POSTGRES_CUSTOM_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_CUSTOM_PASSWORD")
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB")

OWM_API_KEY = os.getenv("OWM_API_KEY")

city = 'Zaragoza'
url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OWM_API_KEY}'


# Do database connection here
retries = 10
while retries > 0:
    try:
        conn = psycopg2.connect(host=POSTGRES_HOST, user=POSTGRES_USER, password=POSTGRES_PASSWORD, dbname=POSTGRES_DB_NAME)
        cursor = conn.cursor()
        print('Successful connection')
        break
    except Exception as e:
        retries -= 1
        print(f'Retry {10 - retries}, exception caught: {e}')
        if retries <= 0:
            print('DB connection error')
            break
        time.sleep(5)


@app.get("/")
def read_root():
    return {"data": "123"}


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def weather_update_loop():
    while True:
        try:
            response = requests.get(url)

            if response.status_code == 200:
                result = response.json()

                # Flatten the JSON and add the timestamp
                flat_result = flatten_json(result)
                flat_result["timestamp"] = datetime.now().strftime("%Y%m%d_%H%M%S")

                data_to_insert = (
                    flat_result.get('dt'),
                    flat_result.get('id'),
                    flat_result.get('cod'),
                    flat_result.get('base'),
                    flat_result.get('name'),
                    flat_result.get('sys_id'),
                    flat_result.get('sys_type'),
                    flat_result.get('timezone'),
                    flat_result.get('wind_deg'),
                    flat_result.get('coord_lat'),
                    flat_result.get('coord_lon'),
                    flat_result.get('main_temp'),
                    flat_result.get('timestamp'),
                    flat_result.get('clouds_all'),
                    flat_result.get('sys_sunset'),
                    flat_result.get('visibility'),
                    flat_result.get('wind_speed'),
                    flat_result.get('sys_country'),
                    flat_result.get('sys_sunrise'),
                    flat_result.get('weather_0_id'),
                    flat_result.get('main_humidity'),
                    flat_result.get('main_pressure'),
                    flat_result.get('main_temp_max'),
                    flat_result.get('main_temp_min'),
                    flat_result.get('weather_0_icon'),
                    flat_result.get('weather_0_main'),
                    flat_result.get('main_feels_like'),
                    flat_result.get('weather_0_description')
                )

                # Insert into the database
                cursor.execute(
                    'INSERT INTO weather_data (dt, city_id, cod, base, name, sys_id, sys_type, timezone, wind_deg, coord_lat, coord_lon, main_temp, timestamp, clouds_all, sys_sunset, visibility, wind_speed, sys_country, sys_sunrise, weather_id, main_humidity, main_pressure, main_temp_max, main_temp_min, weather_icon, weather_main, main_feels_like, weather_description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    data_to_insert
                )
                conn.commit()
                print('Saved data to database')
            else:
                print('No data to save')
                pass

            time.sleep(10)

        except Exception as e:
            print(e)
            pass


weather_update_loop()