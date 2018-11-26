import socket
import threading
from pygame.time import Clock
import sys
import json
sys.path.append('..')
from server.game_server import GameServer


class ServerHandler(socket.socket, threading.Thread):

    BUFFER_SIZE = 2048
    FPS = 60

    def __init__(self, client_ip, server_ip, event_hub):
        # connection setup
        socket.socket.__init__(self)
        threading.Thread.__init__(self)
        # self.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
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
        ch_sock, ch_addr = self.accept()
        self.player_id = self.receive_player_id()

        self.sock = ch_sock
        self.sock.settimeout(None)
        self.sock.setDaemon(True)
        self.sock.bind(client_ip)
        self.server_ip = ch_addr
        # clock = Clock()
        while True:
            # clock.tick(self.FPS)
            try:
                # self.send_client_update_json()
                game_update_json = self.receive_game_update_json()
                self.update_self_attr_from_json(game_update_json)
                self.wait_server()
                self.send_client_update_json()
            except:
                print("server handler {} timed out.".format(self.player_id))
        print("server handler ends")

    def connect(self):
        self.sendto(GameServer.COMMAND_CLIENT_CONNECT.encode(
            'utf-8'), self.server_ip)
        return

    def receive_game_update_json(self):
        # print("receive: 1. receiving update from server")
        try:
            data, address = self.recvfrom(self.BUFFER_SIZE)
        except:
            print("receive: error receiving")
        # print("receive: 2. finish receiving update.")
        if data is None:
            raise ValueError(
                'Unable to receive game update from {}'.format(address))
        # print("receiving from server: {}".format(data.decode('utf-8')))
        decoded_json = data.decode('utf-8')
        self.sock.sendall(GameServer.COMMAND_CLIENT_RECEIVED_UPDATE.encode(
            'utf-8'))
        # print("decoded json: {} from server {}".format(decoded_json, address))
        return decoded_json

    def receive_player_id(self):
        data = self.recv(self.BUFFER_SIZE)
        if data is None:
            return -1
        decoded = data.decode('utf-8')
        try:
            player_id = int(decoded)
            print('player_id', player_id)
        except ValueError as err:
            raise ValueError(err + ' Should have received an integer!')

        # OVERWRITE self.server_address to the one received, since that will be address of the client handler
        return player_id

    def update_self_attr_from_json(self, data_dumped):
        data_json = json.loads(data_dumped)
        # print(data_json["cur_pos"])
        self.cur_pos = data_json["cur_pos"]  # array(tuple(2), tuple(2))
        self.color = data_json["color"]  # array(3)
        self.drawer = data_json["drawer"]  # int
        # obj {"player_1": int, "player_2": int}

        # we actually don't need this. draw right is decided by client handler.
        self.canDraw = (self.player_id == data_json["drawer"])

        self.score = data_json["score"] # later
        self.client_answer = data_json["client_answer"] # later
        self.input_text = data_json["input_txt"] # later
        self.correct = data_json["correct"] # might needed for pause and more....
        
        if self.correct: # later
            self.client_answer = ""
            self.event_hub.client_answer = ""

    def wait_server(self):
        data, addr = self.recvfrom(self.BUFFER_SIZE)
        print('data:', data, 'address_info:', addr)
        if data:
            decoded = data.decode('utf-8')
            if decoded != "ok to update":
                raise ValueError('Expecting "{}", but got "{}"'.format("ok to update", decoded))
            # print('Client address found:',W address_info)
            return addr
    def send_client_update_json(self):
        # print("send: 1. sending client update to server")

        try:
            self.sendto(self.event_hub.to_json().encode('utf-8'), self.server_ip)
        except:
            print("sending update to server failed")
        # print("send: 2. end sending update...")
        return
