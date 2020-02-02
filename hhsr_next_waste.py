import time
import json
import paho.mqtt.client as mqtt

broker_address = "192.168.2.88"     # mqtt Server adresse

def on_connect(client, userdata, flags, rc):
    client.subscribe('/home/mqtt')
    # print("Connected with the result", str(rc))

def on_publish(client, userdata, mid):
    pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(host=broker_address, port=1883, keepalive=60)
# print("Connected to MQTT Broker: ", broker_address)

pubTopic="/home/waste/" # Welches Topic soll bedient werden. 

try:
    with open('data.json', 'r', encoding='utf-8') as f:
        parsed = json.load(f)    
except OSError:
    print('Datei nicht gefunden!')
    raise

# json = json.dumps(parsed, sort_keys=True, indent=4, ensure_ascii=False)

client.loop_start()
for key, value in parsed.items():
    if value['Fällig'] <1:
        client.publish(topic=pubTopic + key.split()[0], payload="1", qos=0, retain=True)
    else: 
        client.publish(topic=pubTopic + key.split()[0], payload="0", qos=0, retain=True)

client.loop_stop()