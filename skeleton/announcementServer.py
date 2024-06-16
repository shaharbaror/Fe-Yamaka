import socket as s
import numpy as np
import time
import nacl

from mainServer import Server
from protocol import Protocol, Encryption
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
uri = "mongodb+srv://shaharbaror1:5CKlFQnQ3rK4TLNe@cluster0.tvuwsdx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


#5CKlFQnQ3rK4TLNe
#shaharbaror1
class DataBase:

    def __init__(self):
        # Connect to the mongodb Server
        self.client = None
        self.database = None
        self.is_connected = False
        self.cities = None

    def connect_to_database(self):
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        try:
            self.database = self.client["fulldb"]
            self.is_connected = True
            return "connection successful"
        except Exception as e:
            print(e)
        return "connection failed"

    def get_all_cities(self):
        locations = self.database["locations"]
        self.cities = locations.find()  # get all of the registered locations from the db

    def get_in_pos(self, position):
        for l in self.cities:
            if l["position-min"] < position < l["position-max"]:
                return l["position"]
        return None


class AnnouncementServer(Server, DataBase):
    def __init__(self, address, port):
        super().__init__(address, port)
        self.projectile_list = []
        self.position_list = []
        self.when_to_check = time.time() + 5
        #need a map of all the places names and their positions

    def alert_city(self, city):
        for p in self.position_list:
            if p["city"] == city:
                self.encryption.send_encrypted_msg("alert", p["client"])

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

        for l in landing_positions:
            city_to_warn = self.get_in_pos(l)
            self.alert_city(city_to_warn)

        # remove all of the old projectiles
        curr_time = time.time()
        if self.when_to_check <= curr_time:
            for p in self.projectile_list:
                if p[1] < curr_time:
                    self.projectile_list.remove(p)
        # add all the extra detections to the list of projectiles
        self.projectile_list.extend(landing_positions)

    def respond(self):
        readable = super().respond()

        if readable:
            for client in readable:
                if client:
                    data = Protocol.receive_messages(client)

                    if data == "newPos":
                        projectiles_detected = Protocol.receive_messages(client)
                        self.calculate_trajectory(projectiles_detected)
                    elif data == "signup":
                        user_data = Protocol.receive_messages(client)
                        self.position_list.append({"city":user_data[0], "client": client, "key": user_data[1]})
                    elif data == "new_key":
                        self.encryption.receive_public_key(client)
                        self.encryption.send_key(client)
                    elif data == "leave":
                        user_data = Protocol.receive_messages(client)
                        self.position_list.remove({"city":user_data[0], "client": client, "key": user_data[1]})


def main():
    server = AnnouncementServer("0.0.0.0", 8001)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()