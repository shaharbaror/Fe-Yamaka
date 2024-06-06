import socket as s
from mainServer import Server
from protocol import Protocol
import numpy as np


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

        distance_between_cameras = 0.16

        def position_of_point(cord1, cord2):
            dist_from_middle1 = cord1[0] - height1
            dist_from_middle2 = cord2[0] - height2

            height_dist1 = (height / 2) - cord1[1]
            height_dist2 = (height / 2) - cord2[1]

            tan_of1 = np.absolute(dist_from_middle1) / height1
            tan_of2 = np.absolute(dist_from_middle2) / height2

            modifier = ((tan_of1 + tan_of2) * (dist_from_middle1 <= 0 <= dist_from_middle2) +
                        (tan_of1 - tan_of2) * (dist_from_middle1 <= 0 and dist_from_middle2 <= 0) +
                        (tan_of2 - tan_of1) * (dist_from_middle1 >= 0 and dist_from_middle2 >= 0))
            z_distance = distance_between_cameras / modifier

            distance_of_cam1 = z_distance / np.cos(np.tanh(tan_of1))
            distance_of_cam2 = z_distance / np.cos(np.tanh(tan_of2))

            y_of_object_cam1 = distance_of_cam1 * np.sin(np.tanh(height_dist1 / height1))
            x_of_object_cam1 = z_distance * tan_of1

            y_of_object_cam2 = distance_of_cam2 * np.sin(np.tanh(height_dist2 / height2))
            x_of_object_cam2 = z_distance * tan_of2
            return [x_of_object_cam1, y_of_object_cam1, z_distance], [x_of_object_cam2, y_of_object_cam2, z_distance]

        for circle1 in cam1_positions:
            for circle2 in cam2_positions:
                if np.absolute(circle1[1] - circle2[1]) < 20:
                    circle1_pos, circle2_pos = position_of_point(cam1_positions, cam2_positions)
                    print(f"""Camera number 1 calculated stats: {circle1_pos}. \n
                           Camera number 2 calculated stats: {circle2_pos}.""")

    def send_message(self, message):
        self.s.send(message)
        data = Protocol.receive_messages(self.s)
        self.calculate_positions(data[0], data[1])





def main():
    calc_client = CalcClient()
    calc_client.send_message()


if __name__ == "__main__":
    main()