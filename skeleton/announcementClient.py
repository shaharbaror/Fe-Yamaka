import socket as s
from protocol import Protocol

class AnnouncementClient:
    def __init__(self, address, port, location):
        self.s = s.socket()
        self.s.connect((address, port))
        self.locations_array = [location]

    def ask_for_extra_data(self):
        message = Protocol.prepare_message("status")
        message += Protocol.prepare_message(Protocol.prepare_message(str(self.locations_array)))
        self.s.send(message)
        response = Protocol.receive_messages(self.s)
        return response

    def run_client(self):
        dangered_locations = self.ask_for_data()
        # need to somehow make it so that the server will only send once in danger and not before
        # The Announcement server has a list of all of the clients to alarm and all to notify.
        # when the client sends "status" they ask to change their notification places
        # The norm is that the client is always listening and once there is a problem then the server sends
