import socket as s
import numpy as np
from protocol import Protocol

from mainServer import Server


class AnnouncementServer(Server):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.projectile_list = []
        #need a map of all the places names and their positions

    def calculate_trajectory(self, projectiles_detected):
        landing_positions = []

        # calculate where and when the object is going to land
        for i in projectiles_detected:
            y_velocity = projectiles_detected[1][1]
            time_left = (y_velocity + np.sqrt(y_velocity ** 2 + 19.62)) / 9.81
            if time_left > 0:
                landing_positions.append(
                    [[i[0][0] + i[1][0] * time_left, 0, i[0][2] + i[1][2] * time_left], i[2] + time_left])

        # verify that the objects found are indeed new and not the same ones
        for i in landing_positions:
            is_on_list = False
            for j in self.projectile_list:
                if np.absolute(np.subtract(i[0], j[0])) < [0.1, 0.1, 0.1] and np.absolute(i[1] - j[1]) < 2:
                    is_on_list = True
            if is_on_list:
                landing_positions.remove(i)

        # add all the extra detections to the list of projectiles
        self.projectile_list.extend(landing_positions)

    def what_to_send_to_client(self, user_data):
        # send the client the data about the projectiles that are heading twards the requested location
        pass

    def respond(self):
        readable = super().respond()

        if readable:
            for client in readable:
                if client:
                    data = Protocol.receive_messages(client)

                    if data == "newPos":
                        projectiles_detected = Protocol.receive_messages(client)
                        self.calculate_trajectory(projectiles_detected)

                    if data == "status":
                        user_data = Protocol.receive_messages(client)
                        client.send_message(Protocol.prepare_message(self.what_to_send_to_client(user_data)))

def main():
    server = AnnouncementServer("0.0.0.0", 8001)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()