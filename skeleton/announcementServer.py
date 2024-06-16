import socket as s
import numpy as np
import time

from mainServer import Server
from protocol import Protocol
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

    # NEEDS DECRYPTION
    # def insert_new_user(self, username, password, locations):
    #     try:
    #         # This whole thing needs to be async since its way too slow
    #         users = self.database["users"]
    #         new_user = users.find_one({"name":username})
    #         if new_user == ([] or None):
    #             try:
    #                 new_user_query = {"username":username, "password": password, "locations":locations, "is_online":1}
    #                 users.insert_one(new_user_query)
    #                 return "insertion succeeded"
    #             except Exception as e:
    #                 print(e)
    #                 return "insertion failed"
    #
    #
    #     except Exception:
    #         return "couldn't add user"
    #     return "sign up successful"
    #
    # def authenticate_user(self, username, password):
    #
    #     try:
    #         users = self.database["users"]
    #         authenticate_user = users.find_one({"username":username,"password":password, "is_online":0})
    #         if authenticate_user == ([] or None):
    #             return "Authentication Failed"
    #         else:
    #             return "Authentication Successful"
    #     except Exception as e:
    #         print(e)
    #         return "Couldn't fetch data"
    #
    # def update_user_status(self, username, password, locations, is_online):
    #     # insert_query = "INSERT INTO users (username, password, locations, is_online) VALUES (%s, %s, %s, %i)"
    #     # try:
    #     #     users_query = f"SELECT * FROM users WHERE username = {username}"
    #     #     self.cursor.execute(users_query)
    #     #     user = self.cursor.fetchall()
    #     #     if user["password"] == password:
    #     #         user_data = (user["username"], user["password"], locations, is_online)
    #     #         self.cursor.execute(insert_query, user_data)
    #     #         self.conn.commit()
    #     #         return "change successful"
    #     #     return "access denied!"
    #     # except Exception:
    #     #     return "change failed"









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
                p["client"].send(Protocol.prepare_message("alert"))

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
                        self.position_list.append({"city":user_data, "client": client})
                    elif data == "leave":
                        user_data = Protocol.receive_messages(client)
                        self.position_list.remove({"city":user_data, "client": client})


def main():
    server = AnnouncementServer("0.0.0.0", 8001)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()