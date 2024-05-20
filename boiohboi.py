import numpy as np
import socket as s

class server:
    def __init__(self):
        self.s = s.socket()


    def start_server(self):
        self.s.bind(("0.0.0.0", 8000))
        self.s.listen(100)

    def get_request(self):
        self.s.accept()