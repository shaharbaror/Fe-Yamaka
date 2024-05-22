import socket as s
from select import select
from protocol import Protocol


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

            for client in readable:
                data = Protocol.receive_messages(client).decode()

                if data == "ready":
                    client.send(Protocol .prepare_message("Snet"))

def main():
    server = Server("0.0.0.0", 8000)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()

