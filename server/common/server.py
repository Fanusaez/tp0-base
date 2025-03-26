import socket
import logging
from common.utils import *
from common.deserialize import *
from common.serialize import *
import time
import sys

class Server:
    def __init__(self, port, listen_backlog, cant_clientes):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None
        self._running = True
        self._clients_socket = {}
        self._finished_clients = []
        self._current_client_id = 0
        self._cant_clientes = cant_clientes

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running:
            try:
                client_socket = self.__accept_new_connection()
                # Handshake with client
                client_id = handshake(client_socket)
                if client_id and client_id not in self._clients_socket and client_socket:
                    # Add to diccionary
                    self._clients_socket[client_id] = client_socket
                    # Set current client id and client socket
                    self._current_client_id = client_id
                    self._client_socket = client_socket
                    self.__handle_client_connection(client_socket)
            except RuntimeError as e:
                logging.error(f"Error in server: {e}")

    def __handle_client_connection(self, client_sock):
        """
        Handle client connection, receving all batches from client
        and store them in database
        """
        try:
            while True:
                bets, success = receive_batch(client_sock)

                # No more batchs, exit loop
                if not bets and success:
                    break
                
                # Batch received
                elif success:
                    logging.info("action: apuesta_recibida | result: success | cantidad: %d", len(bets))
                    send_ack(client_sock)
                    store_bets(bets)

                # Error receiving batch
                else:
                    logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    break

        except OSError as e:
            logging.info(f"action: receive_message | result: fail | cantidad: {len(bets)}")
            raise RuntimeError("Error receiving batch")

        try:
            self.__handle_post_batch_process()
        except:
            logging.info(f"action: sorteo | result: fail")
            raise RuntimeError("Error in post batch process")

    def __handle_post_batch_process(self):
        """
        Handle post batch process:
            - Receives winners request
            - Sends numebrs of winners to client
            - Sends winners to client after all of them finished sending batches
        """
        try:
            # Receive client int ID
            agency_id = receive_winners_request(self._client_socket)

            winners = get_winners_bet(agency_id)
            send_number_of_winners(self._client_socket, len(winners))

            # Receive ACK from client
            if not receive_ack(self._client_socket):
                logging.info("action: receive_ack | result: fail")

            # Client finished sending batches, add it to finished clients
            if self._current_client_id not in self._finished_clients:
                self._finished_clients.append(self._current_client_id)

            if len(self._finished_clients) >= self._cant_clientes:

                logging.info("action: sorteo | result: success")
                for i in range(1, self._cant_clientes + 1):
                    winners_document = get_winners_bet(i)
                    send_winners(self._clients_socket[i], winners_document)
                    # Wait for ACK
                    if not receive_ack(self._clients_socket[i]):
                        logging.error("action: receive_ack | result: fail")
                self.shutdown()
        except RuntimeError as e:
            logging.info("post batch proccess | result: fail")
            raise RuntimeError("Error in post batch process")

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
        self._running = False
        try:
            # Close all client sockets
            for socket in self._clients_socket.values():
                if socket:
                    socket.close()
            logging.info("action: shutdown | result: success")

        except OSError as e:
            logging.error(f"action: shutdown | result: fail | error: {e}")
        finally:
            # Close server socket
            if self._server_socket:
                self._server_socket.close()
            logging.info("Server has been shutdown")


        