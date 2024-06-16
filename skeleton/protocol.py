import socket as s
import nacl
from nacl import public
from nacl.public import Box, PrivateKey, PublicKey
from nacl.utils import random


class Protocol:

    @staticmethod
    def receive_messages(soc: s.socket):
        try:
            length = soc.recv(10).decode()

            if length == '':
                return ''
            length = int(length)

            return soc.recv(length).decode()
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def prepare_message(message):
        """
        This function receives a message and returns it formatted and ready to send
        :param message: The message to prepare
        :type message: str
        :return: bytes
        """
        length = str(len(message)).zfill(10)
        return (f"{length}{message}").encode()


class Encryption:
    def __init__(self):
        self.box = {}     # {f"{key}": box, ...}

        self.private_key = None
        self.public_key = None
        self.receiver_public_keys = []  # [{"socket": socket, "public_key": public_key}, ...]

        self.public_key_bytes = None
        self.private_key_bytes = None

    def create_keys(self):
        # Generate private key
        self.private_key = public.PrivateKey.generate()
        self.public_key = self.private_key.public_key

        # Convert private key to bytes
        self.private_key_bytes = bytes(self.private_key)
        self.public_key_bytes = bytes(self.public_key)

    def find_public_key(self, socket):
        for k in self.receiver_public_keys:
            if k["socket"] == socket:
                return k["public_key"]
        return None

    def decrypt(self, encrypted_message, client):
        # Ensure receiver_public_key is set before decryption
        key = self.find_public_key(client)

        if not key:
            raise ValueError("Receiver public key not set.")
        if not isinstance(self.private_key, PrivateKey):
            raise TypeError("self.private_key must be a PrivateKey.")
        if not isinstance(key, PublicKey):
            raise TypeError("self.receiver_public_key must be a PublicKey.")

        try:
            decrypted_message = self.box[f"{key}"].decrypt(encrypted_message)
            print(f"{decrypted_message =}")
            return decrypted_message.decode('utf-8')
        except nacl.exceptions.ValueError as e:
            print(f"connection error: {e}")
            return "connection error"

    def send_key(self, socket):
        # Serialize public key to send it over the network
        public_key_bytes = self.public_key._bytes_()
        msg = Protocol.prepare_message("new_key") + Protocol.prepare_message(str(public_key_bytes))
        socket.send(msg)

    def receive_public_key(self, socket):
        public_key_bytes = Protocol.receive_messages(socket).encode()
        if len(public_key_bytes) != 32:
            raise ValueError("Public key must be 32 bytes.")
        key_received = PublicKey(public_key_bytes)
        self.receiver_public_keys.append({"socket": socket, "public_key": key_received})
        self.create_box(key_received)


    def create_msg(self, msg, socket) -> bytes:
        # Generate a nonce of 24 bytes
        nonce = random(Box.NONCE_SIZE)
        key = self.find_public_key(socket)
        # Encrypt the message with the generated nonce
        if key:
            return self.box[str(key)].encrypt(msg, nonce)

        # Return nonce + ciphertext
        return b''

    def send_encrypted_msg(self, msg, socket):
        encrypted_msg = self.create_msg(msg)
        msg = Protocol.prepare_message(str(encrypted_msg))
        socket.send(msg)

    def create_box(self, key):
        self.box[f"{key}"] = Box(self.private_key, key)


