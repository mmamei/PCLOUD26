import csv
import json
import time
from pathlib import Path
from requests import post


F_URL = 'https://europe-west8-pcloud2026.cloudfunctions.net/save_data'
CSV_PATH = Path(__file__).with_name('CleanData_PM10.csv')
SENSOR_NAME = 'sensor1'
INTERVAL_SECONDS = 3


with CSV_PATH.open(newline='', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        print(row)
        response = post(
            F_URL,
            data={'data': json.dumps({'datetime': row['datetime'], 'PM10': row['PM10']})},
        )
        print(f"{row['datetime']} -> {response.status_code}")
        time.sleep(INTERVAL_SECONDS)
