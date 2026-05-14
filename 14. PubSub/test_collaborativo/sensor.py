from google.cloud import pubsub_v1
from google.auth import jwt
import json
from topic_subscription_creator import create_topic
import time

service_account_info = json.load(open("secretps.json"))
audience = "https://pubsub.googleapis.com/google.pubsub.v1.Publisher"
credentials = jwt.Credentials.from_service_account_info(service_account_info, audience=audience)
publisher = pubsub_v1.PublisherClient(credentials=credentials)

topic_path = create_topic('sensormarco')

for i in range(100):
    
    val = i % 50
    if i % 10 == 0:
        val += 100

    r = publisher.publish(topic_path,b'message 1',val=f'{val}',key2='val2')
    print(r.result())
    time.sleep(1)
