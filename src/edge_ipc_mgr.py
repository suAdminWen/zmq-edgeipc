from threading import Thread
import json
import time

from . import MQTTClient
from peer_node import PeerNode
from ipcmgr_node import IpcMgrNode


class EdgeIpcMgr(MQTTClient):

    def __init__(self, host, port):
        super(EdgeIpcMgr, self).__init__(host, port)
        self.peers_status = False

    def _on_connect(self, client, userdata, flags, rc):
        print('on_connect ', rc)
        client.subscribe('edge')

    def _on_message(self, client, userdata, msg):
        print('on_message')
        payload = json.loads(msg.payload.decode())
        if 'data' in payload:
            data = payload.get('data')
            if 'services' in data:
                if not self.peers_status:
                    services = data.get('services')
                    self.peers_daemon(services)

    def peers_daemon(self, services):
        evmgr_config = services.get('evmgr')
        mgr_ident = self.create_evmgr(evmgr_config)
        evpusher_ident = self.create_pusher(
            services.get('evpusher')[0], mgr_ident)
        evpuller = self.create_pusher(
            services.get('evpuller')[0], mgr_ident)
        evpuller.send('Hi, I am %s' % evpuller, evpusher_ident)
        self.peers_status = True

    def create_evmgr(self, config):
        evmgr = IpcMgrNode(config.get('sn') + str(config['iid']))
        evmgr.recv_loop()
        return evmgr.ident

    def create_pusher(self, config, mgr_ident):
        ident = config.get('sn') + str(config['iid'])
        evpusher = PeerNode(ident, mgr_ident)
        evpusher.recv_loop()
        evpusher.ready()
        return ident

    def send_cloud_msg(self):
        while True:
            rc, mid = self.publish('cloud', 'register')
            time.sleep(10)


def main():
    client = EdgeIpcMgr('127.0.0.1', 1883)
    client.connect()
    t1 = Thread(target=client.loop)
    t2 = Thread(target=client.send_cloud_msg)
    t1.daemon = True
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
