import zmq
import json
import time

context = zmq.Context()
video_dealer = context.socket(zmq.ROUTER)

video_dealer.setsockopt(zmq.IDENTITY, b'video_pusher')
video_dealer.connect('tcp://localhost:5555')

time.sleep(1)
video_dealer.send_multipart([b'edge_ipc', b'READY'])

while True:
    msg = video_dealer.recv_multipart()

    video_dealer.send_multipart([b'edge_ipc', b'video_ml', b'HELLO'])

    try:
        msg = msg[1].decode()
        msg_dict = json.loads(msg)
        if 'cmd' in msg_dict:
            print('接收命令：', msg_dict.get('cmd'))
    except json.decoder.JSONDecodeError:
        print('接收到消息 ', msg)
