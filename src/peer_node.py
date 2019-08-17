import zmq
import time
import json
from threading import Thread


def encode(data):
    if not isinstance(data, bytes):
        data = data.encode()
    return data


class PeerNode:
    context = zmq.Context()

    pusher = context.socket(zmq.ROUTER)
    poller = zmq.Poller()

    def __init__(self, ident, edge_ipc):

        self.ident = ident
        self.pusher.setsockopt(zmq.IDENTITY, encode(ident))
        self.pusher.connect('tcp://localhost:5555')
        self.edge_ipc = encode(edge_ipc)
        self.poller.register(self.pusher, zmq.POLLIN)

    def ready(self):
        self.send('READY')

    def send(self, data, addr=None):

        data = encode(data)
        if addr:
            addr = encode(addr)
            data = [self.edge_ipc, addr, data]
            print(self.ident + ': 消息将会被%s转发给%s' % (self.edge_ipc, addr))
        else:
            data = [self.edge_ipc, data]
            print(data)
            print(self.ident + ': 消息发送给 %s' % (self.edge_ipc,))
        self.pusher.send_multipart(data)

    def loop(self):
        while True:
            # 我只是一个不停止的循环
            pass

    def recv_loop(self):
        # 单开线程，不会阻塞
        t = Thread(target=self._recv_loop)
        t.daemon = False
        t.start()

    def _recv_loop(self):

        while True:
            msg = self.pusher.recv_multipart()
            if len(msg) == 2:
                [addr, msg] = msg
                data, rc = self._to_json(msg.decode())
                if rc and 'cmd' in data:
                    print(self.ident + ': 收到命令：', data.get('cmd'))
                else:
                    print(self.ident + ': 收到来自 %s 的信息：%s' % (addr, msg))
            else:
                print(self.ident + ': 非法信息', msg)

    def _to_json(self, data):
        try:
            r_dict = json.loads(data)
        except json.decoder.JSONDecodeError:
            return data, False
        else:
            return r_dict, True


if __name__ == '__main__':
    pusher_node = PeerNode('ILS-13', 'ILS-11')
    pusher_node.recv_loop()
    pusher_node.ready()
    while True:
        pusher_node.ready()
        time.sleep(2)
        # pusher_node.send('I am ILS_13', 'ILS-12')
