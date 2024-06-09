import socket
from mainServer import Server
from protocol import Protocol


class DataServer (Server):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.alert_server = None

    def respond(self):
        readable = super().respond()

        if readable:
            for client in readable:
                if client:
                    data = Protocol.receive_messages(client)
                    if data == "im alert":
                        self.alert_server = client
                    if data == "ball cords":
                        cords = Protocol.receive_messages(client)
                        print(cords)
                        #self.alert_server.send(Protocol.prepare_message("newPos") + Protocol.prepare_message(cords))

def main():
    data_server = DataServer("0.0.0.0", 8010)
    while data_server.running:
        data_server.accept_connections()
        data_server.respond()

if __name__ == "__main__":
    main()