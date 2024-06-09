import socket as s
import numpy as np
import mysql.connector
import json

from mainServer import Server
from protocol import Protocol
class DataBase:
    def __int__(self):
        # Connect to the MySQL server
        self.conn = mysql.connector.connect(
            host="localhost",
            user="your_username",
            password="your_password",
            database="your_database"
        )

        self.cursor = self.conn.cursor()

        # Create a table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            locations TEXT
                        )''')

        # Commit changes
        self.conn.commit()

    # NEEDS DECRYPTION
    def insert_new_user(self, username, password, locations):
        try:
            users_query = f"SELECT * FROM users WHERE first_letter = {username[0]}"
            self.cursor.execute(users_query)
            rows = self.cursor.fetchall()
            if any(d["username"] == username for d in rows):
                return "username already exist"

            insert_query = "INSERT INTO users (username, password, locations, is_online) VALUES (%s, %s, %s, %i)"
            user_data = (username, password, json.dumps(locations), 1)

            # insert into the database
            self.cursor.execute(insert_query, user_data)
            self.conn.commit()

            # insert user data into the location query
            location_query = f"INSERT INTO locations (username, password, locations, is_online) VALUES (%s, %s, %s, %i)"

        except Exception:
            return "couldn't add user"
        return "sign up successful"

    def authenticate_user(self, username, password):
        insert_query = "INSERT INTO users (username, password, locations, is_online) VALUES (%s, %s, %s, %i)"
        try:
            users_query = f"SELECT * FROM users WHERE username = {username}"
            self.cursor.execute(users_query)
            user = self.cursor.fetchall()

            if user["password"] == password:
                user_data = (user["username"], user["password"], user["locations"], 1)
                self.cursor.execute(insert_query, user_data)
                self.conn.commit()
                return "Login Successful"
        except Exception:
            return "Couldn't fetch data"

    def update_user_status(self, username, password, locations, is_online):
        insert_query = "INSERT INTO users (username, password, locations, is_online) VALUES (%s, %s, %s, %i)"
        try:
            users_query = f"SELECT * FROM users WHERE username = {username}"
            self.cursor.execute(users_query)
            user = self.cursor.fetchall()
            if user["password"] == password:
                user_data = (user["username"], user["password"], locations, is_online)
                self.cursor.execute(insert_query, user_data)
                self.conn.commit()
                return "change successful"
            return "access denied!"
        except Exception:
            return "change failed"





class AnnouncementServer(Server, DataBase):
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
                    elif data == "signup":
                        user_data = Protocol.receive_messages(client)
                        self.insert_new_user(user_data["username"], user_data["password"], user_data["locations"])
                    elif data == "authenticate":
                        user_data = Protocol.receive_messages(client)
                        self.authenticate_user(user_data["username"], user_data["password"])
                    elif data == "change":
                        user_data = Protocol.receive_messages(client)
                        self.update_user_status(user_data["username"], user_data["password"], user_data["locations"], user_data["is_online"])


def main():
    server = AnnouncementServer("0.0.0.0", 8001)
    while server.running:
        server.accept_connections()
        server.respond()

if __name__ == "__main__":
    main()