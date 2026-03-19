# For this example we rely on the Paho MQTT Library
# for Python
# You can install it through the following command:
# pip install paho-mqtt

import paho.mqtt.client as mqtt
import time
import csv
from pathlib import Path

# The callback for when the client receives a CONNACK response from the server.
def marco_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


client_id = "client1"
broker_ip = 'broker.emqx.io'
broker_port = 1883

default_topic = "/sensors/pm10/1"

mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = marco_connect

print("Connecting to "+ broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()

csv_path = Path(__file__).with_name("CleanData_PM10.csv")

with csv_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
    reader = csv.DictReader(csv_file)
    for row_number, row in enumerate(reader, start=1):
        payload_string = f"{row['datetime']},{row['PM10']}"
        infot = mqtt_client.publish(default_topic, payload_string)
        infot.wait_for_publish()
        print(
            f"Message Sent: {row_number} Topic: {default_topic} Payload: {payload_string}"
        )
        time.sleep(1)

mqtt_client.loop_stop()