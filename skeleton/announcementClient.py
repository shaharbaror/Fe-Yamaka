import socket as s
from protocol import Protocol, Encryption
import tkinter as tk
from tkinter import messagebox

# class AnnouncementClient:
#     def __init__(self, address, port, location = None):
#         self.s = s.socket()
#         # self.s.connect((address, port))
#         self.locations_array = [location]
#         self.is_running = True
#         self.is_authenticated = False
#
#
#     def ask_for_extra_data(self):
#         message = Protocol.prepare_message("status")
#         message += Protocol.prepare_message(Protocol.prepare_message(str(self.locations_array)))
#         self.s.send(message)
#         response = Protocol.receive_messages(self.s)
#         return response
#
#     def log_in_page(self):
#
#         def authenticate():
#             username = username_entry.get()
#             password = password_entry.get()
#
#             if 10 > len(username) > 0 and 10 > len(password) > 0:
#                 self.is_authenticated = True
#                 print("authentication successfull!")
#                 exit_app()
#                 return
#             elif username and password:
#                 messagebox.showwarning("Input Error", "your username/password are longer than 10 characters")
#             else:
#                 messagebox.showwarning("Input Error", "Please fill out both fields")
#             return
#
#         def exit_app():
#             root.destroy()
#             self.is_running = False
#
#         root = tk.Tk()
#
#         root.title("Login Page")
#         root.geometry("300x200")
#
#         username_label = tk.Label(root, text='Username')
#         username_label.pack(pady=5)
#         username_entry = tk.Entry(root)
#         username_entry.pack(pady=5)
#
#         password_label = tk.Label(root, text='Password')
#         password_label.pack(pady=5)
#         password_entry = tk.Entry(root, show="*")
#         password_entry.pack(pady=5)
#
#         login_button = tk.Button(root, text="Login", command=authenticate)
#         login_button.pack(pady=5)
#
#         # Create and place the exit button
#         exit_button = tk.Button(root, text="Exit", command=exit_app)
#         exit_button.pack(pady=5)
#
#
#         root.mainloop()
#
#     def show_menu(self):
#         locations = [
#             {"id": 1, "name": "Location A"},
#             {"id": 2, "name": "Location B"},
#             {"id": 3, "name": "Location C"},
#             {"id": 4, "name": "Location D"},
#         ]
#         current_locations = [{"id": 2, "name": "Location B"}]
#
#         def get_more_data():
#             root.withdraw()  # Hide the main window
#             new_window = tk.Toplevel()
#             new_window.title("More Data on Locations")
#             new_window.geometry("1240x1080")
#
#             # need to FETCH the locations from the database
#
#
#             def back_to_main():
#                 new_window.destroy()
#                 root.deiconify()  # Show the main window again
#
#                 # Function to handle the select button click
#
#             def select_location():
#                 try:
#                     selected_index = location_listbox.curselection()[0]
#                     selected_location = locations[selected_index]
#                     if selected_location not in current_locations:
#                         current_locations.append(selected_location)
#
#                 except IndexError:
#                     messagebox.showwarning("Selection Error", "Please select a location from the list")
#
#             def remove_location():
#                 try:
#                     selected_index = location_listbox.curselection()[0]
#                     selected_location = locations[selected_index]
#                     if selected_location in current_locations:
#                         current_locations.remove(selected_location)
#                 except Exception:
#                     messagebox.showwarning("Selection Error", "Please Select A locaiton that is on your list")
#
#             data_label = tk.Label(new_window, text="Select a location from the list below:", font=("Helvetica", 14))
#             data_label.pack(pady=10)
#             current_label = tk.Label(new_window, text='locations you have')
#             current_label.pack(pady=5)
#             current_locations_listbox = tk.Listbox(new_window, height=10)
#             for current_location in current_locations:
#                 current_locations_listbox.insert(tk.END, f"ID:{current_location['id']} - Name: {current_location['name']}")
#             current_locations_listbox.pack(pady=10)
#             other_label = tk.Label(new_window, text='locations you can have')
#             other_label.pack(pady=5)
#             location_listbox = tk.Listbox(new_window, height=10)
#             for location in locations:
#                 location_listbox.insert(tk.END, f"ID: {location['id']} - Name: {location['name']}")
#             location_listbox.pack(pady=10)
#
#             # Create and place a select button in the new window
#             select_button = tk.Button(new_window, text="Select Location", command=select_location)
#             select_button.pack(pady=5)
#
#             remove_button = tk.Button(new_window, text="remove Location", command=remove_location)
#             remove_button.pack(pady=5)
#
#             # Create and place a back button in the new window
#             back_button = tk.Button(new_window, text="Back to Main Menu", command=back_to_main)
#             back_button.pack(pady=5)
#
#         root = tk.Tk()
#
#         root.title("Main Menu")
#         root.geometry("1240x1080")
#
#         title_label = tk.Label(root, text="Fe-Yamaka", font=("Helvetica", 24))
#         title_label.pack(pady=20)
#
#         # Create and place the button
#         data_button = tk.Button(root, text="Get More Data on Locations", command=get_more_data)
#         data_button.pack(pady=120)
#
#         root.mainloop()
#
#
#     def run_client(self):
#         self.log_in_page()
#         if self.is_authenticated:
#             self.show_menu()
#         #dangered_locations = self.ask_for_data()
#         # need to somehow make it so that the server will only send once in danger and not before
#         # The Announcement server has a list of all of the clients to alarm and all to notify.
#         # when the client sends "status" they ask to change their notification places
#         # The norm is that the client is always listening and once there is a problem then the server sends
#         pass
#

class AlertClient:
    def __init__(self, address, port, location = None):
        self.s = s.socket()
        self.s.connect((address, port))
        self.location = location
        self.is_running = True
        self.encryption = Encryption(self.s)
        self.encryption.create_keys()

    def setup_encryption(self):
        self.encryption.send_key()
        response = Protocol.receive_messages(self.s)
        print(response)
        if response == "send_key":
            self.encryption.receive_public_key()
            print("block")
            self.encryption.create_box()


    def register_to_server(self):

        self.setup_encryption()
        order = Protocol.prepare_message(self.encryption.create_msg("signup".encode()), True)
        values = Protocol.prepare_message(self.encryption.create_msg(str(self.location).encode()), True)
        self.s.send(order + values)
        print("here")

    def run(self):

        self.register_to_server()

        while True:
            try:
                enc_message = Protocol.receive_messages(self.s, False)
                decr_message = self.encryption.decrypt(enc_message)
                if decr_message == "alert":
                    print("ALERT")
                elif decr_message == "stop":
                    print("no alert")
            except Exception as e:
                print(e)




def main():
    # announcemnet_client = AnnouncementClient("0.0.0.0", 8002)
    # announcemnet_client.run_client()
    # alert_client = AlertClient("172.16.20.69", 8001, "Tel-Aviv")
    alert_client = AlertClient("127.0.0.1", 8001, "Netanya")
    alert_client.run()

if __name__ == "__main__":
    main()
