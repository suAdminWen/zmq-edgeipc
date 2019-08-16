import time
from paho.mqtt.client import Client


def on_connect(client, userdata, flags, rc):
    print('on_connect')
    client.subscriber('cloud')
    client.subscriber('report')


def on_message(client, userdata, msg):
    print('on_message')
    payload = msg.payload.decode()
    print(payload)


client = Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect('127.0.0.1', 1883)

client.loop_start()

client.publish('edge', 'cmd')
time.sleep(3)
