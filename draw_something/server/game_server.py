import socket
from random import randint
from time import sleep

from server.client_handler import ClientHandlerG as ClientHandler
from server.huffman_handler import HuffmanHandler
from server.event_hub import EventHub


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]
    return ip_addr


class GameServerG:
    def __init__(self):
        self.sock_for_setup = socket.socket()
        self.sock_for_setup.setblocking(True)  # no timeout.
        self.ip = get_ip_address()
        try:
            self.sock_for_setup.bind((self.ip, 12345))
        except:
            self.sock_for_setup.bind((self.ip, 12346))

        self.player_num = int(input("Enter number of players: "))
        self.sock_for_setup.listen(self.player_num)  # listens on public:12345

        print("listening on address {}".format((self.ip, '12345')))
        self.ch_list = []
        self.eh = EventHub()

        hh = HuffmanHandler()
        self.entries = hh.get_entries()
        self.eh.entries = self.entries
        self.eh.player_num = self.player_num
        self.choose_random_entry()
        self.eh.answer = self.eh.selected_entry[0]
        # now server event_hub has access to entries(answers)

    def choose_random_entry(self):
        entriesLen = len(self.eh.entries)
        chosenEntry = str(randint(1, entriesLen))
        self.eh.selected_entry = self.eh.entries[chosenEntry]
        print(self.eh.selected_entry)
        return

    def start(self):
        # set up connection, initialize two client_handler that takes the incoming socket and does updatings.
        # 1. send the client socket their id
        for player in range(1, self.player_num + 1):
            (client_sock, client_ip) = self.sock_for_setup.accept()
            ch = ClientHandler(client_sock, player, self.eh)
            self.ch_list.append(ch)
            print(player)

        # sleep so that client don't receive data mixed together.
        sleep(1)

        for ch in self.ch_list:
            ch.start()

        while True:
            sleep(1000)  # stand by so the client handler threads don't die.
        return
