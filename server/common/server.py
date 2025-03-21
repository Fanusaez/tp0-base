import socket
import logging
import struct
from common.utils import *
from common.deserialize import *

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

        while self.running:
            client_socket = self.__accept_new_connection()
            if client_socket:
                self._client_socket = client_socket
                self.__handle_client_connection(client_socket)

    def __handle_client_connection(self, client_sock):
        """
        Maneja múltiples batchs de apuestas por una única conexión cliente.
        Finaliza cuando el cliente cierra la conexión o se detecta un error grave.
        """
        try:
            while True:
                bets, success = receive_batch(client_sock)

                # No more batchs, exit loop
                if not bets and success:
                    logging.info(f"action: exit | result: success")
                    break
                
                # Batch received
                elif success:
                    logging.info(f"action: apuesta_recibida | result: success | cantidad: {len(bets)}")
                    # for bet in bets:
                    #     store_bet(bet)

                    # Send Ack
                    client_sock.sendall("ACK\n".encode("utf-8"))
                else:
                    logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    break

        except OSError as e:
            logging.info(f"action: receive_message | result: success | cantidad: {len(bets)}")
        finally:
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

        