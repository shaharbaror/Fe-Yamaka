import socket as s
from mainServer import Server
from protocol import Protocol


class CalcServer (Server):
    pass


class CalcClient:
    def __init__(self):
        self.s = s.socket()
        self.s.connect(("127.0.0.1", 8000))

    def send_message(self):
        self.s.send(Protocol.prepare_message("ready"))
        print("sent")
        data = Protocol.receive_messages(self.s)
        print(data)


def main():
    calc_client = CalcClient()
    calc_client.send_message()


if __name__ == "__main__":
    main()