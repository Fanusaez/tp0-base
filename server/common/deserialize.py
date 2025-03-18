
from common.utils import *


def recive_bet(client_sock):
        """Reads a bet from a client socket and creates a Bet object"""
        bet = Bet(
            agency = int(read_field(client_sock)),
            first_name = read_field(client_sock),
            last_name = read_field(client_sock),
            document = read_field(client_sock),
            birthdate = read_field(client_sock),
            number = int(read_field(client_sock)),
        )
        return bet

def read_field(sock):
        """Reads 2 bytes from socket indicating the length of the field and then reads the field"""
        length_data = recive_all(sock, 2)  # Leer los primeros 2 bytes (longitud)
        if not length_data:
            return None

        # Convert 2 bytes to integer
        bytes_to_read = (length_data[0] << 8) | length_data[1]

        data = recive_all(sock, bytes_to_read).decode("utf-8")
        return data

def recive_all(client_socket, bytes_to_receive):
        """Reads exactly bytes_to_receive bytes from client_socket"""
        data = b""
        while len(data) < bytes_to_receive:
            packet = client_socket.recv(bytes_to_receive - len(data))
            if not packet:
                return None
            data += packet
        return data
