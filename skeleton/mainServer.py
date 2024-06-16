import json
import random
import socket as s
from select import select
from protocol import Protocol, Encryption
from main3 import Maskinator
import multiprocessing
import imutils
import time




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
        self.encryption = Encryption()
        self.encryption.create_keys()

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

    def respond(self):
        readable = super().respond()
        received_axis = [None,None]
        axis_counter = 0
        if readable:
            for client in readable:
                if client:
                    data = Protocol.receive_messages(client)

                    # if data == circAxis the camera client has sent the coordinates of the circles they found
                    if data == "circCords":
                        axis = Protocol.receive_messages(client)
                        time_of_cords = Protocol.receive_messages(client)
                        print(f"Got Cords: {axis}")
                        # add the coordinates and increase the counter
                        if axis[0] == [1]:
                            received_axis[0] = [axis[1:], time_of_cords]
                        else:
                            received_axis[1] = [axis[1:], time_of_cords]

                        axis_counter += 1
                    if data == "give_key":
                        self.encryption.send_encrypted_msg(str(self.encryption.public_key_bytes), client)
                    elif data == "ready_calculate":
                        self.encryption.send_encrypted_msg(str(self.linked_list.value), client)
                        self.linked_list = self.linked_list.next_block

            if axis_counter > 1:
                #  call the client that calculates positions ____________________________________
                self.pos.next_block = LinkedList(received_axis)
                self.pos = self.pos.next_block

                if not self.linked_list.value:
                    self.linked_list = self.linked_list.next_block

            axis_counter = 0
            received_axis = []


def main():
    server = MainServer("0.0.0.0", 8000)
    while server.running:
        server.accept_connections()
        server.respond()


if __name__ == "__main__":
    main()
