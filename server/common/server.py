import socket
import logging
import struct
from common.utils import *

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None
        self.running = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # TODO: Modify this program to handle signal to graceful shutdown
        # the server
        while self.running:
            client_socket = self.__accept_new_connection()
            if client_socket:
                self._client_socket = client_socket
                self.__handle_client_connection(client_socket)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """

        try:
            bet = self.__recive_bet(client_sock)
            #addr = client_sock.getpeername()
            store_bets([bet])
            logging.info(f"action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}")
            
            # Send acknoledgement to client
            client_sock.sendall("ACK\n".encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            # Close client socket after exchanging messages
            client_sock.close()

    def __accept_new_connection(self):
        """ 
        Accept new connections with proper error handling 
        """
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            return None  # Retorna None si el socket se cerró
        
    def __read_field(self, sock):
        """Reads 2 bytes from socket indicating the length of the field and then reads the field"""
        length_data = self.__recive_all(sock, 2)  # Leer los primeros 2 bytes (longitud)
        if not length_data:
            return None

        length = struct.unpack("!H", length_data)[0]  # Desempacar como entero (Big Endian)
        data = self.__recive_all(sock, length).decode("utf-8")  # Leer los bytes del campo y decodificarlos
        return data
    
    def __recive_all(self, client_socket, bytes_to_receive):
        """Reads exactly bytes_to_receive bytes from client_socket"""
        data = b""
        while len(data) < bytes_to_receive:
            packet = client_socket.recv(bytes_to_receive - len(data))
            if not packet:
                return None
            data += packet
        return data


    def __recive_bet(self, client_sock):
        """Reads a bet from a client socket and creates a Bet object"""
        bet = Bet(
            agency = int(self.__read_field(client_sock)),
            first_name =  self.__read_field(client_sock),
            last_name = self.__read_field(client_sock),
            document = self.__read_field(client_sock),
            birthdate = self.__read_field(client_sock),
            number = int(self.__read_field(client_sock)),
        )
        return bet

    def shutdown(self):
        """
        Shutdown server socket

        Method to close server socket and client socket if posible
        """
        self.running = False
        try:
            if self._client_socket:
                self._client_socket.close()
            logging.info("action: shutdown | result: success")
        except OSError as e:
            logging.error(f"action: shutdown | result: fail | error: {e}")
        finally:
            self._server_socket.close()
            logging.info("Server has been shutdown")

        