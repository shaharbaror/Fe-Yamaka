import json
import random
import socket as s

import numpy as np
from select import select
from protocol import Protocol, Encryption
from main3 import Maskinator
import multiprocessing
import imutils
import time
from ast import literal_eval




class LinkedList:
    def __init__(self, value = None, next_block = None):
        self.value = value
        self.next_block = next_block

class Server:
    def __init__(self, address, port):
        """

        :param address: Servers address
        :param port: The port the server sits on

        :type address: str
        :type port: int
        """

        self.port = port
        self.address = address
        self.s = s.create_server((address, port))
        self.s.listen(9)
        self.clients = {}
        self.running = True

    def accept_connections(self):

        readable, _, _ = select([self.s], [], [], 0.01)

        if self.s in readable:
            connection, address = self.s.accept()
            self.clients.update({connection: address})

    def respond(self):
        if len(self.clients.keys()) > 0:
            readable, _, _ = select(self.clients.keys(), [], [], 0.01)
            return readable


class MainServer(Server):
    def __init__(self, address, port):
        """
            :param address: Servers address
            :param port: The port the server sits on

            :type address: str
            :type port: int
        """
        super().__init__(address, port)
        self.linked_list = LinkedList()
        self.pos = self.linked_list
        self.timer = [time.time() - 333, time.time() - 666]
        self.s2 = s.socket()
        self.s2.connect(("172.16.6.128",8002))


    def respond(self):
        readable = super().respond()
        received_axis = [None, None]
        axis_counter = 0
        latest_update = time.time()
        if readable:
            for client in readable:
                if client:
                    data = Protocol.receive_messages(client)

                    # if data == circAxis the camera client has sent the coordinates of the circles they found
                    if data == "circCords":
                        axis = literal_eval( Protocol.receive_messages(client))
                        time_of_cords =literal_eval( Protocol.receive_messages(client))
                        camera_position = literal_eval(Protocol.receive_messages(client))
                        print(f"Got Cords: {axis}")
                        # add the coordinates and increase the counter

                        if time_of_cords - latest_update >= 1:
                            received_axis = [None, None]

                        if axis[0] == [1]:
                            print("axus", axis[1])
                            received_axis[0] = [axis[1], time_of_cords, camera_position]
                            self.timer[0] = time_of_cords
                            latest_update = time.time()
                        else:
                            print("axiux", axis[1])
                            received_axis[1] = [axis[1], time_of_cords, camera_position]
                            self.timer[1] = time_of_cords
                            latest_update = time.time()




            jus = np.absolute(self.timer[1] - self.timer[0])
            print(jus)
            if jus < 50 and received_axis[0] and received_axis[1]:

                print("here")
                #  call the client that calculates positions ____________________________________
                self.pos.next_block = LinkedList(received_axis)
                self.pos = self.pos.next_block
                self.linked_list = self.linked_list.next_block
                print(self.linked_list.value)

                self.s2.send(Protocol.prepare_message("yus") + Protocol.prepare_message(str(self.linked_list.value)))


            axis_counter = 0



def main():
    server = MainServer("0.0.0.0", 8000)
    while server.running:
        server.accept_connections()
        server.respond()


if __name__ == "__main__":
    main()
