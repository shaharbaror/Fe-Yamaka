import socket as s
from mainServer import Server
from protocol import Protocol
import numpy as np
import time
from ast import literal_eval





class LinkedList:
    def __init__(self, value = None, nextItem = None):
        self.value = value
        self.nextItem = nextItem


class CalcClient:
    def __init__(self):
        self.s = s.socket()
        self.s.connect(("172.16.20.69", 8000))
        # Also connect to the second server

        self.s2 = s.socket()
        self.s2.connect(("127.0.0.1", 8002))




    def send_message(self, message):
        self.s.send(message)
        data = Protocol.receive_messages(self.s)
        return data

    def run_client(self):
        list1 = LinkedList()
        pos1 = list1
        count = 0
        while True:
            # send a request for main server to give new cords. returns: [[cam1,time], [cam2,time]]
            returned_value = self.send_message("ready_calculate")


class CalcServer(Server):
    def __init__(self, address, port):
        # super().__init__(address, port)
        self.list1 = LinkedList()
        self.pos1 = self.list1
        self.count = 0
        self.s2 = s.socket()
        self.s2.connect(("127.0.0.1", 8001))

    def calculate_positions(self, cam1_positions, cam2_positions):  # [[[x,y]], time, camera postion]
        cam01_positions = []
        cam02_positions = []

        print("cam1", cam1_positions)
        print("cam2", cam2_positions)

        width1 = 1240   # depends on the width of the frame
        width2 = 1240
        height = 1080   # height of the frame
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

            if z_distance <= 0:
                return None, None
            distance_of_cam1 = z_distance / np.cos(np.tanh(tan_of1))
            distance_of_cam2 = z_distance / np.cos(np.tanh(tan_of2))

            y_of_object_cam1 = distance_of_cam1 * np.sin(np.tanh(height_dist1 / np.sqrt(height1**2 + dist_from_middle1**2)))
            x_of_object_cam1 = z_distance * tan_of1

            y_of_object_cam2 = distance_of_cam2 * np.sin(np.tanh(height_dist2 / np.sqrt(height2**2 + dist_from_middle2**2)))
            x_of_object_cam2 = z_distance * tan_of2
            return [x_of_object_cam1, y_of_object_cam1, z_distance], [x_of_object_cam2, y_of_object_cam2, z_distance]

        for circle1 in cam1_positions[0]:
            for circle2 in cam2_positions[0]:
                print(f"{circle1} is a circle \n {circle2} is also a circle")
                if np.absolute(circle1[1] - circle2[1]) < 20:
                    circle1_pos, circle2_pos = position_of_point(circle1, circle2)
                    print(f"ahoo {circle1_pos} ahoo {circle2_pos}")
                    if circle1_pos and circle2_pos:
                        cam01_positions.append([circle1_pos + cam1_positions[2], cam1_positions[1]])   # [positions, time of record]
                        cam02_positions.append([circle2_pos + cam2_positions[2], cam2_positions[1]])
                    print(f"""Camera number 1 calculated stats: {circle1_pos}. \n
                           Camera number 2 calculated stats: {circle2_pos}.""")
        return cam01_positions, cam02_positions

    def identify_projectiles(self, position1, position2, position3):
        time_between_frame12 = position2[1] - position1[1]
        time_between_frame23 = position3[1] - position2[1]
        gravity = -9.81
        accelaration_calc = gravity * (time_between_frame23 ** 2) / 2
        mistake_modifier = [0.1, 0.1, 0.1]

        # find y speed:
        def verification(frame1, frame2):
            """
            :param frame1: The position of the object in frame 1
            :param frame2: The position of the object in frame 2
            :param frame3: The position of the object in frame 3
            """
            # since the velocity is the delta velocity
            # the calculation WILL be wrong since its not really the speed on frame 2
            vector_velocity = [(frame2[0] - frame1[0]) / time_between_frame12,
                               (frame2[1] - frame1[1]) / time_between_frame12,
                               (frame2[2] - frame1[2]) / time_between_frame12]  # calculate the x,y,z velocity
            estimated_position = []
            estimated_position[0] = frame2[0] + vector_velocity[0] * time_between_frame23
            # x1 = x0 + v0*t + at^(2) / 2
            estimated_position[1] = (frame2[1] + vector_velocity[1] * time_between_frame23 + accelaration_calc)

            estimated_position[2] = frame2[2] + vector_velocity[2] * time_between_frame23

            # calculate how far is the ball from the estimation, if it is close:
            # then return the ball as an object with position, time of record, and velocity
            for frame3 in position3:
                if np.absolute(np.subtract(estimated_position, frame3)) < mistake_modifier:
                    # [[x, y, z], [Vx, Vy, Vz], time of record]
                    return [frame2, vector_velocity, position2[1]]
            return None

        balls_to_return = []

        for ball1 in position1:
            for ball2 in position2:
                is_ball = verification(ball1, ball2)
                if is_ball:
                    balls_to_return.append(is_ball)

        return balls_to_return



    def respond(self):
        # readable = super().respond()
        # if readable:
        #     for client in readable:
        #         if client:
        #             data = Protocol.receive_messages(client)
        #
        #             if data != "":
        #                 print(data)
        #             if data == "yus":
        #
        #                 returned_value = literal_eval(Protocol.receive_messages(client))
        #                 print("returned value: ", returned_value)
        #                 new_coordinates1, new_coordinates2 = self.calculate_positions(returned_value[0],
        #                                                                               returned_value[1])
        #                 print("coord",new_coordinates1)
        #                 if len(new_coordinates1) > 0:
        #                     self.pos1.nextItem = LinkedList(new_coordinates1)
        #                     self.pos1 = self.pos1.nextItem
        #
        #                     if self.count >= 3:
        #
        #                         self.list1 = self.list1.nextItem
        #                         # now start calculating trajectory of the object
        #                         projectiles_to_alarm = self.identify_projectiles(self.list1.value, self.list1.nextItem.value,
        #                                                                          self.pos1.value)
        #                         print(f"these projectiles are real: {projectiles_to_alarm}")
        #                         if projectiles_to_alarm:
        #                             # after the projectiles had been identified, send them back to the server
        #                             # self.s2.send(Protocol.prepare_message("newPos") + Protocol.prepare_message(
        #                             #     str(projectiles_to_alarm)))
        #                             print(projectiles_to_alarm)
        #
        #                     self.count += 1

        # [(x, y, z), (Vx, Vy, Vz), time of record]
        self.s2.send(Protocol.prepare_message("newPos") + Protocol.prepare_message(str([[[1, 1, 1], [1.33, 2.5, 0], time.time()]])))


def main():
    # calc_client = CalcClient()
    # calc_client.run_client()
    calc_server = CalcServer("0.0.0.0", 8001)
    calc_server.respond()


if __name__ == "__main__":
    main()