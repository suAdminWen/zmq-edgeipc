from paho.mqtt.client import Client
from threading import Thread
import zmq
import json
import time
from random import randint

context = zmq.Context()
edge_router = context.socket(zmq.ROUTER)
edge_router.setsockopt(zmq.IDENTITY, b'edge_ipc')
edge_router.bind('tcp://*:5555')


def on_connect(client, userdata, flags, rc):
    print('on_connect ', rc)
    client.subscribe('edge')


def on_message(client, userdata, msg):
    print('on_message')
    payload = msg.payload.decode()
    print('I 接收MQTT云端命令', payload)
    if payload == 'cmd':
        data = {
            'cmd': ['STOP', 'START'][randint(0, 1)],
            'time': time.time()
        }
        edge_router.send_multipart(
            [b'video_pusher', json.dumps(data).encode()])


def mqtt_client():

    client = Client()
    client.username_pw_set('admin', 'password')
    client.connect('127.0.0.1', 1883)
    client.on_connect = on_connect
    client.on_message = on_message

    client.loop_start()

    return client


def zmq_server(client):

    poller = zmq.Poller()
    poller.register(edge_router, zmq.POLLIN)
    while True:
        socks = dict(poller.poll())
        if socks.get(edge_router) == zmq.POLLIN:
            msg = edge_router.recv_multipart()
            if len(msg) == 3:
                msg = msg[1:]
                print('I 做了一次转发信息给%s' % msg[0])
                edge_router.send_multipart(msg)
            elif msg[-1] == b'READY':
                print('%s 设备准备完毕' % msg[0])
                edge_router.send_multipart([msg[0], b'Update Config'])
            else:
                print('%s 发送信息 %s' % (msg[0], msg[-1]))


def send_cloud_msg(client):
    while True:
        rc, mid = client.publish('cloud', 'register')
        time.sleep(10)


def main():
    client = mqtt_client()
    t1 = Thread(target=zmq_server, args=(client,))
    t2 = Thread(target=send_cloud_msg, args=(client,))
    t1.daemon = True
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
