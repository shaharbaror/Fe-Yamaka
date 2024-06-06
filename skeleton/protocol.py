import socket as s


class Protocol:

    @staticmethod
    def receive_messages(soc: s.socket):
        length = soc.recv(10).decode()

        if length == '':
            return ''
        length = int(length)

        return soc.recv(length).decode()

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

