import socket as s
import nacl
from nacl import public
from nacl.public import Box, PrivateKey, PublicKey
from nacl.utils import random


class Protocol:

    @staticmethod
    def receive_messages(soc: s.socket, decode=True):

        try:

            length = soc.recv(10).decode()


            if length == '':
                return ''
            length = int(length)

            if decode:

                msg = soc.recv(length).decode()
                print(msg)
                return msg
            else:
                msg = soc.recv(length)
                print(msg)
                return msg

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
    def __init__(self, socket):
        self.box = None
        self.socket = socket
        self.private_key = None
        self.public_key = None
        self.receiver_public_key = None
        self.public_key_bytes = None
        self.private_key_bytes = None

    def create_keys(self):
        # Generate private key
        self.private_key = public.PrivateKey.generate()
        self.public_key = self.private_key.public_key

        # Convert private key to bytes
        self.private_key_bytes = bytes(self.private_key)
        self.public_key_bytes = bytes(self.public_key)

    def decrypt(self, encrypted_message):
        # Ensure receiver_public_key is set before decryption
        if not self.receiver_public_key:
            raise ValueError("Receiver public key not set.")
        if not isinstance(self.private_key, PrivateKey):
            raise TypeError("self.private_key must be a PrivateKey.")
        if not isinstance(self.receiver_public_key, PublicKey):
            raise TypeError("self.receiver_public_key must be a PublicKey.")

        try:
            decrypted_message = self.box.decrypt(encrypted_message)
            print(f"{decrypted_message =}")
            return decrypted_message.decode('utf-8')
        except nacl.exceptions.ValueError as e:
            print(f"connection error: {e}")
            return "connection error"

    def send_key(self):
        # Serialize public key to send it over the network
        public_key_bytes = self.public_key._bytes_()
        msg = Protocol.prepare_message(public_key_bytes)
        self.socket.send(msg)

    def receive_public_key(self):
        public_key_bytes = Protocol.receive_messages(self.socket)
        if len(public_key_bytes) != 32:
            raise ValueError("Public key must be 32 bytes.")
        self.receiver_public_key = PublicKey(public_key_bytes)

    def create_msg(self, msg) -> bytes:
        # Generate a nonce of 24 bytes
        nonce = random(Box.NONCE_SIZE)

        # Encrypt the message with the generated nonce
        encrypted_msg = self.box.encrypt(msg, nonce)

        # Return nonce + ciphertext
        return encrypted_msg

    def send_encrypted_msg(self, msg):
        encrypted_msg = self.create_msg(msg)
        msg = str(len(encrypted_msg)).zfill(10).encode() + encrypted_msg
        self.socket.send(msg)

    def create_box(self):
        self.box = Box(self.private_key, self.receiver_public_key)