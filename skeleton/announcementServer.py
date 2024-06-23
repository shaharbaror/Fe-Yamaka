import socket as s
import numpy as np
import time
import nacl

from mainServer import Server
from protocol import Protocol, Encryption
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from ast import literal_eval
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
        self.client_list = []
        #need a map of all the places names and their positions

    def alert_city(self, city):
        for p in self.position_list:
            if p["city"] == city:
                p["enc"].send_encrypted_msg("alert", p["client"])

    def calculate_trajectory(self, projectiles_detected):
        landing_positions = []

        # calculate where and when the object is going to land
        print(projectiles_detected)
        for i in projectiles_detected:
            print(f"ai ai ai {i}")
            y_velocity = i[1][1]
            time_left = (y_velocity + np.sqrt(y_velocity ** 2 + 19.62)) / 9.81
            print(f"the land of the ones time: {time_left}")
            print(i)
            if time_left > 0:
                pos = [[i[0][0] + i[1][0] * time_left, 0, i[0][2] + i[1][2] * time_left], i[2] + time_left]
                print(f"pos pos pos {pos}")
                landing_positions.append( pos
                    )

        # verify that the objects found are indeed new and not the same ones
        for i in landing_positions:
            is_on_list = False
            for j in self.projectile_list:
                if np.absolute(np.subtract(i[0], j[0])) < [0.1, 0.1, 0.1] and np.absolute(i[1] - j[1]) < 2:
                    is_on_list = True
            if is_on_list:
                landing_positions.remove(i)

        # for l in landing_positions:
        #     city_to_warn = self.get_in_pos(l)
        #     self.alert_city(city_to_warn)

        # remove all of the old projectiles
        curr_time = time.time()
        if self.when_to_check <= curr_time:
            for p in self.projectile_list:
                if p[1] < curr_time:
                    self.projectile_list.remove(p)
        # add all the extra detections to the list of projectiles
        self.projectile_list.extend(landing_positions)
        print(self.projectile_list)

    def respond(self):
        readable = super().respond()

        if readable:
            for client in readable:
                if client:

                    data = Protocol.receive_messages(client, False)
                    client_enc = None
                    if data:

                        for c in self.client_list:

                            if c["client"] == client:
                                client_enc = c["enc"]

                        if client_enc is not None:
                            data = client_enc.decrypt(data)

                        if data == "newPos":
                            projectiles_detected = literal_eval(Protocol.receive_messages(client))
                            self.calculate_trajectory(projectiles_detected)

                        elif data == "signup":

                            user_data = Protocol.receive_messages(client, False)

                            user_data = client_enc.decrypt(user_data)

                            self.position_list.append({"city": user_data, "client": client, "enc": client_enc})

                        elif data == b"send_key":
                            new_Encryption = Encryption(client)
                            new_Encryption.create_keys()

                            new_Encryption.receive_public_key()

                            new_Encryption.create_box()

                            new_Encryption.send_key()

                            self.client_list.append({"client": client, "enc": new_Encryption})
                            print("appended!", self.client_list)



def main():
    server = AnnouncementServer("0.0.0.0", 8001)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()