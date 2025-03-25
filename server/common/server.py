import socket
import logging
from common.utils import *
from common.deserialize import *
from common.serialize import *
import time
import threading

class Server:
    def __init__(self, port, listen_backlog, cant_clientes):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True
        self._clients_socket = {}
        self._finished_clients = []
        self._cant_clientes = cant_clientes
        self._lock_fclients = threading.Lock()
        self._lock_bets = threading.Lock()
        self._threads = []

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running :
            try:
                client_socket = self.__accept_new_connection()
                if not client_socket:
                    continue
                
                # Handshake with client
                client_id = handshake(client_socket)

                if client_id and client_id not in self._clients_socket:
                    # Add to diccionary
                    self._clients_socket[client_id] = client_socket

                # Start thread to handle client
                thread = threading.Thread(
                    target=self.__handle_client_thread,
                    args=(client_id, client_socket),
                    daemon=True
                )
                thread.start()
                self._threads.append(thread)
            
            except RuntimeError as e:
                logging.error(f"Error in server: {e}")
                
    def __handle_client_thread(self, client_id, client_sock):
        """
        Handle client connection, receving all batches from client
        and store them in database
        """
        try:
            while True:
                bets, success = receive_batch(client_sock)

                # No more batchs, exit loop
                if not bets and success:
                    self.__handle_post_batch_process(client_id, client_sock)
                    break
                
                # Batch received
                elif success:
                    #logging.info("action: apuesta_recibida | result: success | cantidad: %d", len(bets))
                    send_ack(client_sock)
                    with self._lock_bets:
                        store_bets(bets)

                # Error receiving batch
                else:
                    logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                    break
        
        except OSError as e:
            logging.info(f"action: receive_message | result: fail | cantidad: {len(bets)}")
            raise RuntimeError("Error receiving batch")

    def __handle_post_batch_process(self, client_id, client_socket):
        """
        Handle post batch process:
            - Receives winners request
            - Sends numebrs of winners to client
            - Sends winners to client after all of them finished sending batches
        """
        try:
            # Receive client int ID
            agency_id = receive_winners_request(client_socket)
            with self._lock_bets:
                winners = get_winners_bet(agency_id)
            send_number_of_winners(client_socket, len(winners))

            # Receive ACK from client
            if not receive_ack(client_socket):
                logging.info("action: receive_ack | result: fail")

            # Client finished sending batches, add it to finished clients
            with self._lock_fclients:
                self._finished_clients.append(client_id)
                # Check if all clients finished sending batches
                if len(self._finished_clients) >= self._cant_clientes:
                    threading.Thread(target=self.__handle_agencies_sort, daemon=True).start()

        except RuntimeError as e:
            logging.info("post batch proccess | result: fail")
            raise RuntimeError("Error in post batch process")

    def __handle_agencies_sort(self):
        """tbw"""
        try: 
            logging.info("action: sorteo | result: success")
            for i in range(1, self._cant_clientes + 1):
                winners_document = get_winners_bet(i)
                send_winners(self._clients_socket[i], winners_document)
                # Wait for ACK
                if not receive_ack(self._clients_socket[i]):
                    logging.error("action: receive_ack | result: fail")
            self.shutdown()
        except RuntimeError as e:
            logging.info("sort proccess | result: fail")
            raise RuntimeError("Error in sort process")

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
            for thread in self._threads:
                thread.join()
        except OSError as e:
            logging.error(f"action: shutdown | result: fail | error: {e}")
        finally:
            # Close server socket
            if self._server_socket:
                self._server_socket.close()
            logging.info("Server has been shutdown")


        