# For this example we rely on the Paho MQTT Library
# for Python
# You can install it through the following command:
# pip install paho-mqtt

import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a CONNACK response from the server.
def marco_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


client_id = "client1"
broker_ip = 'broker.emqx.io'
broker_port = 1883

default_topic = "/pcloud2025reggioemilia/test/1"

mqtt_client = mqtt.Client(client_id)
mqtt_client.on_connect = marco_connect

print("Connecting to "+ broker_ip + " port: " + str(broker_port))
mqtt_client.connect(broker_ip, broker_port)

mqtt_client.loop_start()

message_limit = 1000
for message_id in range(message_limit):
    payload_string = f'message {message_id}'
    infot = mqtt_client.publish(default_topic, payload_string)
    infot.wait_for_publish()
    print(f"Message Sent: {message_id} Topic: {default_topic} Payload: {payload_string}")
    time.sleep(1)

mqtt_client.loop_stop()