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
from typing import List
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
            return "connection successful", True
        except Exception as e:
            print(e)
        return "connection failed", False

    def get_all_cities(self):
        locations = self.database["locations"]
        self.cities = locations.find()  # get all of the registered locations from the db

    def get_in_pos(self, position):
        print("posi pos pos",position[0])

        for l in self.cities:
            print(f"the first position is between {l["position-min"]} and {l["position-max"]}")
            print(f"also {l["position-min"] < position[0]} and {l["position-max"] > position[0]}")
            if l["position-min"] < position[0] < l["position-max"]:
                city_name = l["city"]
                return city_name
        return None


class AnnouncementServer(Server, DataBase):
    def __init__(self, address, port):
        Server.__init__(self, address, port)
        DataBase.__init__(self)
        
        self.projectile_list = []
        self.position_list = []
        self.when_to_check = time.time() + 5
        self.client_list = []
        #need a map of all the places names and their positions



    def alert_city(self, city):
        for p in self.position_list:
            if p["city"] == city:
                print("found city")
                message = p["enc"].create_msg(b"alert")
                p["client"].send(Protocol.prepare_message(message, True))

    def calculate_trajectory(self, projectiles_detected):

        # remove all of the old projectiles
        curr_time = time.time()
        if self.when_to_check <= curr_time:
            for p in self.projectile_list:
                if p[1] < curr_time:
                    self.projectile_list.remove(p)


        landing_positions = []

        # calculate where and when the object is going to land

        for i in projectiles_detected:

            y_velocity = i[1][1]
            time_left = (y_velocity + np.sqrt(y_velocity ** 2 + 19.62)) / 9.81


            if time_left > 0:
                pos = [[i[0][0] + i[1][0] * time_left, 0, i[0][2] + i[1][2] * time_left], i[2] + time_left]

                landing_positions.append( pos
                    )

        # verify that the objects found are indeed new and not the same ones
        for i in landing_positions:
            is_on_list = False
            for j in self.projectile_list:

                position_of_landing =list(np.absolute(np.subtract(i[0], j[0])))


                if position_of_landing < [0.1, 0.1, 0.1] and np.absolute(i[1] - j[1]) < 2:
                    is_on_list = True
            if is_on_list:
                print("removed")
                landing_positions.remove(i)

        for l in landing_positions:
            print("in here")
            print(l)
            city_to_warn = self.get_in_pos(l)
            print("got cities to warn", city_to_warn)
            self.alert_city(city_to_warn)

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

                        if data == b"newPos":
                            projectiles_detected = literal_eval(Protocol.receive_messages(client))
                            self.calculate_trajectory(projectiles_detected)

                        elif data == "signup":

                            user_data = Protocol.receive_messages(client, False)

                            user_data = client_enc.decrypt(user_data)
                            print("got to here")

                            self.position_list.append({"city": user_data, "client": client, "enc": client_enc})
                            print("added: ", self.position_list)

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
    while not server.is_connected:
        message, server.is_connected = server.connect_to_database()
        print(message)
    server.get_all_cities()
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()