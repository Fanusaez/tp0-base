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
        self.running = True
        self.clients_socket = {}
        self.finished_clients = []
        self.current_client_id = 0
        self.cant_clientes = cant_clientes

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        for i in range(self.cant_clientes):
            try:
                client_socket = self.__accept_new_connection()
                client_id = handshake(client_socket)
                if client_id and client_id not in self.clients_socket:
                    self.clients_socket[client_id] = client_socket
                    self.current_client_id = client_id
                if client_socket:
                    self._client_socket = client_socket
                    self.__handle_client_connection(client_socket)
            except:
                return None

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
                    #logging.info("action: apuesta_recibida | result: success | cantidad: %d", len(bets))
                    # Send Ack
                    client_sock.sendall("ACK\n".encode("utf-8"))

                    store_bets(bets)
                else:
                    logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    break

        except OSError as e:
            logging.info(f"action: receive_message | result: fail | cantidad: {len(bets)}")

        try:
            agency_id = receive_winners_request(client_sock)
            winners = get_winners_bet(agency_id)
            send_number_of_winners(client_sock, len(winners))

            if not receive_ack(client_sock):
                logging.info("action: receive_ack | result: fail")
                return
        
            # Client finished sending batches
            if self.current_client_id not in self.finished_clients:
                self.finished_clients.append(self.current_client_id)

            if len(self.finished_clients) == self.cant_clientes:
                # dormir 1 seg
                #time.sleep(1)
                logging.info("action: sorteo | result: success")
                for i in range(1, self.cant_clientes + 1):
                    winners = get_winners_bet(i)
                    send_winners(self.clients_socket[i], winners)
                    if not receive_ack(self.clients_socket[i]):
                        logging.info("action: receive_ack | result: fail")
                        return
                self.shutdown()
        except:
            logging.info(f"action: sorteo | result: fail")
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
            for socket in self.clients_socket.values():
                if socket:
                    socket.close()
            logging.info("action: shutdown | result: success")

        except OSError as e:
            logging.error(f"action: shutdown | result: fail | error: {e}")
        finally:
            if self._server_socket:
                self._server_socket.close()
            logging.info("Server has been shutdown")


        