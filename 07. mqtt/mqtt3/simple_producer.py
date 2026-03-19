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
    client.subscribe(control_topic)


def marco_message(client, userdata, msg):
    global is_sending
    payload = msg.payload.decode().strip().lower()
    if payload == "stop":
        is_sending = False
        print("Received STOP on topic control. Sending paused.")
    elif payload == "start":
        is_sending = True
        print("Received START on topic control. Sending resumed.")


client_id = "client1"
broker_ip = 'broker.emqx.io'
broker_port = 1883

default_topic = "/sensors/pm10/1"
control_topic = "control"
is_sending = True

mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = marco_connect
mqtt_client.on_message = marco_message

print("Connecting to "+ broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()

csv_path = Path(__file__).with_name("CleanData_PM10.csv")


# leggi il file CSV e mettili in una lista di dizionari
with csv_path.open(mode="r", encoding="utf-8", newline="") as csv_file:
    reader = csv.DictReader(csv_file)
    rows = list(reader)

i = 0
while i < len(rows):
    if not is_sending:
        time.sleep(1)
        continue
    row = rows[i]
    payload_string = f"{row['datetime']},{row['PM10']}"
    infot = mqtt_client.publish(default_topic, payload_string)
    infot.wait_for_publish()
    print(
        f"Message Sent: {i} Topic: {default_topic} Payload: {payload_string}"
    )
    i += 1
    time.sleep(1)
       
mqtt_client.loop_stop()