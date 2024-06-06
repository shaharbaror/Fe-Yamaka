import socket as s
from mainServer import Server
from protocol import Protocol


class CalcServer (Server):
    pass


class CalcClient:
    def __init__(self):
        self.s = s.socket()
        self.s.connect(("127.0.0.1", 8000))

    def calculate_positions(self, cam1_positions, cam2_positions): # [[x,y], time]
        width1 = 1240
        width2 = 1240
        height = 1080
        height1 = width1 / 2
        height2 = width2 / 2

        def position_of_point(cord1, cord2):
            dist_from_middle1 = cord1[0] - height1
            dist_from_middle2 = cord2[0] - height2

            height_dist1 = (height / 2) - cord1[1]
            height_dist2 = (height / 2) - cord2[1]

    def send_message(self):
        data = Protocol.receive_messages(self.s)





def main():
    calc_client = CalcClient()
    calc_client.send_message()


if __name__ == "__main__":
    main()