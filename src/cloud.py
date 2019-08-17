import time
import json
from paho.mqtt.client import Client

data = {
    "code": 0,
    "time": 0,
    "data": {
        "ipc": "172.31.0.51",
        "username": "admin",
        "password": "FWBWTU",
        "services": {
            "evmgr": {
                "sn": "ILS-1",
                "addr": "0.0.0.0",
                "port-pub": 5556,
                "port-rep": 5557,
                "iid": 1
            },
            "evpuller": [{
                "sn": "ILS-2",
                "addr": "0.0.0.0",
                "port-pub": 5556,
                "port-rep": 5557,
                "iid": 2
            }],
            "evpusher": [{
                "sn": "ILS-3",
                "addr": "localhost",
                "iid": 2,
                "enabled": 1,
                "urlDest": "rtsp://40.73.41.176:554/test1"
            }],
            "evslicer": [{
                "sn": "ILS-4",
                "addr": "192.168.0.25",
                "iid": 3,
                "path": "/var/lib/slices/"
            }],
            "evml": [{
                "feature": "motion",
                "sn": "ILS-5",
                "addr": "192.168.0.26",
                "iid": 4
            }]
        }
    }
}


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

client.publish('edge', json.dumps(data))
time.sleep(3)
