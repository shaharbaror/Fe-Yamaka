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

        self.cam1 = Maskinator("../3DCameras/cam01/recording03_Trim.mp4")
        self.cam2 = Maskinator("../3DCameras/cam02/recording01_Trim.mp4")

    def respond(self):
        readable = super().respond()

        for client in readable:
            if client:
                data = Protocol.receive_messages(client)

                if data == "ready":
                    startof = time.time()
                    frame_cam1, mask_cam1 = self.cam1.get_frame()
                    frame_cam2, mask_cam2 = self.cam2.get_frame()

                    new_mask = []
                    mask_counter = 0
                    new_mask2 = []
                    mask_counter2 = 0
                    for row in range(len(mask_cam2)):
                        if 255 not in mask_cam2[row]:
                            mask_counter += 1
                        else:
                            if mask_counter != 0:
                                new_mask.append([mask_counter])
                            new_mask.append(mask_cam2[row])
                            mask_counter = 0
                        if 255 not in mask_cam1[row]:
                            mask_counter2 += 1
                        else:
                            if mask_counter2 != 0:
                                new_mask2.append([mask_counter2])
                            new_mask2.append(mask_cam1[row])
                            mask_counter2 = 0

                    frame_send_struct = ("{" + f'''
                        
                        "cam1_mask": {new_mask},
                        
                        "cam2_mask": {new_mask2}
''' + "}")
                    endof = time.time()
                    print(endof - startof)
                    print(len(frame_send_struct))
                    client.send(Protocol.prepare_message(frame_send_struct))


def main():
    server = MainServer("0.0.0.0", 8000)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()

