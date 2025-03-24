import socket
import logging
from common.utils import *
from common.deserialize import *
from common.serialize import *
import time
import sys

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None
        self.running = True
        self.clients_socket = {}
        self.finished_clients = []
        self.current_client_id = 0

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self.running:
            client_socket = self.__accept_new_connection()
            client_id = handshake(client_socket)
            if client_id and client_id not in self.clients_socket:
                self.clients_socket[client_id] = client_socket
                self.current_client_id = client_id
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
                    break
                
                # Batch received
                elif success:
                    logging.info("action: apuesta_recibida | result: success | cantidad: %d", len(bets))
                    # Send Ack
                    client_sock.sendall("ACK\n".encode("utf-8"))

                    store_bets(bets)
                else:
                    logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    break

        except OSError as e:
            logging.info(f"action: receive_message | result: fail | cantidad: {len(bets)}")

        agency_id = receive_winners_request(client_sock)
        winners = get_winners_bet(agency_id)
        send_number_of_winners(client_sock, len(winners))

        receive_ack(client_sock)
        
        # Client finished sending batches
        if self.current_client_id not in self.finished_clients:
            self.finished_clients.append(self.current_client_id)

        if len(self.finished_clients) == 5:
            # dormir 1 seg
            #time.sleep(1)
            logging.info("action: sorteo | result: success")
            for i in range(1, 6):
                winners = get_winners_bet(i)
                send_winners(self.clients_socket[i], winners)
                if receive_ack(self.clients_socket[i]):
                    logging.info(f"action: ack_winners | result: success")
                    self.clients_socket[i].close()
            self._client_socket = None
            self.shutdown()


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

            # Forzar flush a stdout/stderr
            for handler in logging.root.handlers:
                handler.flush()
            sys.stdout.flush()
            sys.stderr.flush()

        except OSError as e:
            logging.error(f"action: shutdown | result: fail | error: {e}")
        finally:
            self._server_socket.close()
            logging.info("Server has been shutdown")
            for handler in logging.root.handlers:
                handler.flush()


        