#!/usr/bin/env python

import random
import pygame
import time
import socket

from server.event_hub import EventHub
from utils import *
from client.sh import ServerHandlerG as ServerHandler


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]
    return ip_addr

def client_main():

    # pygame initialization
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill(BGCOLOR)
    pygame.display.set_caption("Draw Something!")
    pygame.init()
    font = pygame.font.Font(None, 32)

    # svh init - communication with server
    server_addr = (input("server ip address: "), 12345) # need to get server from user input
    local_addr = (get_ip_address(), random.randint(10000, 20000))

    local_event_hub = EventHub()
    svh = ServerHandler(local_event_hub, local_addr, server_addr)
    svh.start()

    # state variables
    mouseDown = False
    prevPos = (None, None)

    # wait for server setup
    while svh.canDraw is None: time.sleep(0.1)

    # game start
    clock = pygame.time.Clock()
    once = True
    while True:
        # print("in game loop")
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif not svh.canDraw and event.type == pygame.KEYDOWN:
                parse_input_event(event, local_event_hub)
            else:
                mouseDown, prevPos = parse_drag_event(event, mouseDown, prevPos)

        # just to make this shorter.
        prevPos = update_cursors_from_mouseDown(mouseDown, prevPos, local_event_hub)
        # print(svh.correct, svh.score, svh.input_text)
        
        # now cur_pos is syncd with server.
        pos = svh.cur_pos # [(x, y), (prev_x, prev_y)]
        input_txt = svh.input_txt
        # print(svh.client_answer)
        # draw lines according to two points.
        draw_the_drags_from_pos(pos, screen)
        draw_input_from_eh(input_txt, screen, font)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()