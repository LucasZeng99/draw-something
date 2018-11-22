import socket
import threading
import sys
import json
sys.path.append('..')

from server.game_server import GameServer


class ServerHandler(socket.socket, threading.Thread):

    BUFFER_SIZE = 2048

    def __init__(self, client_ip, server_ip, event_hub):
        # connection setup
        socket.socket.__init__(self, type=socket.SOCK_DGRAM)
        threading.Thread.__init__(self)
        self.settimeout(None)
        self.setDaemon(True)
        self.bind(client_ip)
        self.server_ip = server_ip

        # local client handler vars
        self.player_id = -1
        # used to upload sketches and drawing out on local.(in main)
        self.event_hub = event_hub
        self.canDraw = None

        # local game arguments, used to draw received sketches.
        self.cur_pos = None
        self.color = None
        self.drawer = None
        self.score = None

    def run(self):
        self.connect()
        self.player_id = self.receive_player_id()

        while True:
            game_update_json = self.receive_game_update_json()
            self.update_pygame_from_json(game_update_json)
            self.send_client_update_json()

    def connect(self):
        self.sendto(GameServer.COMMAND_CLIENT_CONNECT.encode(
            'utf-8'), self.server_ip)
        return

    def receive_game_update_json(self):
        data, address = self.recvfrom(self.BUFFER_SIZE)
        if data is None:
            raise ValueError(
                'Unable to receive game update from {}'.format(address))
        decoded_json = data.decode('utf-8')

        # print("decoded json: {} from server {}".format(decoded_json, address))
        return decoded_json

    def receive_player_id(self):
        data, address = self.recvfrom(self.BUFFER_SIZE)
        if data is None:
            return -1
        decoded = data.decode('utf-8')
        try:
            player_id = int(decoded)
            print('player_id', player_id)
        except ValueError as err:
            raise ValueError(err + ' Should have received an integer!')

        # OVERWRITE self.server_address to the one received, since that will be address of the client handler
        self.server_ip = address

        return player_id

    def update_pygame_from_json(self, data_dumped):
        data_json = json.loads(data_dumped)

        # print(data_json)
        # print("updating pygame.")

        self.cur_pos = data_json["cur_pos"]  # array(2)
        self.color = data_json["color"]  # array(3)
        self.drawer = data_json["drawer"]  # int
        # obj {"player_1": int, "player_2": int}
        self.score = data_json["score"]

        self.canDraw = (self.player_id == self.drawer)

    def send_client_update_json(self):
        self.sendto(self.event_hub.to_json().encode('utf-8'), self.server_ip)
        return
