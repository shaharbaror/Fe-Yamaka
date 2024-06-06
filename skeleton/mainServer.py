import json
import socket as s
from select import select
from protocol import Protocol
from main3 import Maskinator
import multiprocessing
import imutils
import cv2 as cv
import time


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


class MainServer (Server):
    def __init__(self, address, port):
        """
            :param address: Servers address
            :param port: The port the server sits on

            :type address: str
            :type port: int
        """
        super().__init__(address, port)

    def respond(self):
        readable = super().respond()

        received_axis = []
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

                        received_axis.append([axis, time_of_cords])

                        axis_counter += 1


                if axis_counter > 1:
                    #  call the client that calculates positions ____________________________________
                    pass
                axis_counter = 0
                received_axis = []





def main():
    server = MainServer("0.0.0.0", 8000)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()

