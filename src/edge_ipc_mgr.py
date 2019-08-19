import json
import time

from mqtt import MQTTClient
from peer_node import PeerNode
from ipcmgr_node import IpcMgrNode


class EdgeIpcMgr(MQTTClient):

    def __init__(self, host, port):
        super(EdgeIpcMgr, self).__init__(host, port)
        self.peers_status = False
        self.peers = {}
        self.evmgr = None

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
        evmgr_config = services.pop('evmgr')
        self.create_evmgr(evmgr_config)

        # 根据配置创建同辈节点
        for peer_config in services.values():
            if isinstance(peer_config, list):
                for config in peer_config:
                    self.create_peer(config)
            elif isinstance(peer_config, dict):
                self.create_peer(peer_config)
            else:
                raise

        # self.create_peer(services.get('evpusher')[0])
        # self.create_peer(services.get('evpuller')[0])
        # self.create_peer(services.get('evslicer')[0])
        # self.create_peer(services.get('evml')[0])

    def create_evmgr(self, config):
        ident = config.get('sn') + str(config['iid'])
        if not self.evmgr:
            self.evmgr = IpcMgrNode(ident)
            self.evmgr.recv_loop()
        return self.evmgr

    def create_peer(self, config):
        ident = config.get('sn') + str(config['iid'])
        if ident in self.peers:
            return

        peer_node = PeerNode(ident, self.evmgr.ident)
        peer_node.recv_loop()
        peer_node.ready()

        self.peers[ident] = peer_node

    def send_cloud_msg(self):
        while True:
            rc, mid = self.publish('cloud', 'register')
            time.sleep(10)


def main():
    client = EdgeIpcMgr('127.0.0.1', 1883)
    client.connect()
    client.loop()


if __name__ == '__main__':
    main()
