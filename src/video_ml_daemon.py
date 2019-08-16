import zmq
import time

context = zmq.Context()
video_ml = context.socket(zmq.ROUTER)

video_ml.setsockopt(zmq.IDENTITY, b'video_ml')
video_ml.connect('tcp://localhost:5555')

time.sleep(1)
video_ml.send_multipart([b'edge_ipc', b'READY'])
video_ml.send_multipart([b'edge_ipc', b'video_pusher', b'video_ml READY'])

while True:
    msg = video_ml.recv_multipart()
    print(msg)
