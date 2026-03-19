from flask import Flask, jsonify, request, render_template
from flask_mqtt import Mqtt

app = Flask(__name__)

database = []

# MQTT Configuration
app.config['MQTT_BROKER_URL'] = 'broker.emqx.io'  # Change to your broker
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TOPIC'] = '/sensors/pm10/#'

mqtt = Mqtt(app)

# Flask route
@app.route('/')
def home():


    data = [["Year", "Values"]]
    for entry in database:
        try:
            datetime_str, pm10_value = entry.split(",")
            year = datetime_str.split(" ")[0].split("-")[0]  # Estrae l'anno
            data.append([year, float(pm10_value)])  # Aggiunge l'anno e il valore PM10 alla lista
        except Exception as e:
            print(f"Errore nel parsing dell'entry '{entry}': {e}")
    return render_template('graph.html', data=str(data))

@app.route('/show')
def show():
    return str(database)

# Callback for MQTT message received
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    msg_payload = message.payload.decode()
    print(f"Received MQTT message: {msg_payload} on topic {message.topic}")
    database.append(msg_payload)  
    print("Current Database State:", database)
    # ['2020-01-01 00:00:00,42.0', ....]
    return 'ok'


# Flask route to handle MQTT-triggered action
@app.route('/mqtt_callback', methods=['POST'])
def mqtt_callback(data=None):
    if data is None:
        data = request.json  # Get data from request if manually triggered
    print(f"Flask received MQTT callback: {data}")
    return jsonify({"status": "success", "received_data": data})

# Subscribe to MQTT topic on startup
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    mqtt.subscribe(app.config['MQTT_TOPIC'])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)