import csv
import time
from pathlib import Path

from requests import post


BASE_URL = 'https://pcloud2026.appspot.com'
CSV_PATH = Path(__file__).with_name('CleanData_PM10.csv')
SENSOR_NAME = 'sensor1'
INTERVAL_SECONDS = 3


with CSV_PATH.open(newline='', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        response = post(
            f'{BASE_URL}/sensors/{SENSOR_NAME}',
            data={'data': row['datetime'], 'val': row['PM10']},
        )
        print(f"{row['datetime']} -> {response.status_code}")
        time.sleep(INTERVAL_SECONDS)
