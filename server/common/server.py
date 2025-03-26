import socket
import logging
from common.utils import *
from common.deserialize import *
from common.serialize import *
import multiprocessing
from multiprocessing import Manager
from time import sleep

class Server:
    def __init__(self, port, listen_backlog, cant_clientes):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._running = True
        self._clients_socket = {}
        self._cant_clientes = cant_clientes
        self._count_down = cant_clientes

        manager = multiprocessing.Manager()
        self._lock_fclients = manager.Lock()
        self._lock_bets = manager.Lock()
        self._barrier = manager.Barrier(cant_clientes)

        self._processes = []

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._running and self._count_down > 0:
            try:
                client_socket = self.__accept_new_connection()
                if not client_socket:
                    continue
                
                # Update number of clients (see better solution)
                self._count_down -= 1

                # Handshake with client
                client_id = handshake(client_socket)

                if client_id and client_id not in self._clients_socket:
                    # Add to diccionary
                    self._clients_socket[client_id] = client_socket

                # Start thread to handle client
                p = multiprocessing.Process(
                    target=handle_client_process,
                    args=(client_socket, client_id, self._lock_bets, self._barrier)
                    )
                p.start()
                self._processes.append(p)
            
            except OSError as e:
                logging.Info(f"ERROR in server: {e}")
                break 

        # Join all processes
        for p in self._processes:
            p.join()

        # Shutdown server
        self.shutdown()

    def __accept_new_connection(self):
        logging.info('action: accept_connections | result: in_progress')
        try:
            self._server_socket.settimeout(1.0)  # timeout de 1 segundo
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except socket.timeout:
            return None
        except OSError:
            return None

    
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
        except OSError as e:
            logging.error(f"action: shutdown | result: fail | error: {e}")
        finally:
            # Close server socket
            if self._server_socket:
                self._server_socket.close()
            logging.info("Server has been shutdown")


def handle_client_process(client_sock, client_id, lock_bets, barrier):
    """
    Handle client connection, receving all batches from client
    and store them in database
    """
    try:
        while True:
            bets, success = receive_batch(client_sock)

            # No more batchs, exit loop
            if not bets and success:
                handle_post_batch_process(client_sock, lock_bets)
                barrier.wait()
                handle_agencies_sort(client_sock, client_id, lock_bets)
                break
            
            # Batch received
            elif success:
                logging.info("action: apuesta_recibida | result: success | cantidad: %d", len(bets))
                send_ack(client_sock)
                with lock_bets:
                    store_bets(bets)

            # Error receiving batch
            else:
                logging.info(f"action: apuesta_recibida | result: fail | cantidad: {len(bets)}")
                break
        
    
    except OSError as e:
        logging.info(f"action: receive_message | result: fail | cantidad: {len(bets)}")
        raise RuntimeError("Error receiving batch")


def handle_post_batch_process(client_socket, lock_bets):
    """
    Handle post batch process:
        - Receives winners request
        - Sends numebrs of winners to client
        - Sends winners to client after all of them finished sending batches
    """
    try:
        # Receive client int ID
        agency_id = receive_winners_request(client_socket)
        with lock_bets:
            winners = get_winners_bet(agency_id)
        send_number_of_winners(client_socket, len(winners))

        # Receive ACK from client
        if not receive_ack(client_socket):
            logging.info("action: receive_ack | result: fail")

    except RuntimeError as e:
        logging.info("post batch proccess | result: fail")
        raise RuntimeError("Error in post batch process")
    

def handle_agencies_sort(client_socket, client_id, lock_bets):
    """Get from id and send winners to client"""
    try: 
        logging.info("action: sorteo | result: success")
        
        # Send winners
        with lock_bets:
            winners_document = get_winners_bet(client_id)
        send_winners(client_socket, winners_document)

        # Wait for ACK
        if not receive_ack(client_socket):
            logging.error("action: receive_ack | result: fail")

    except RuntimeError as e:
        logging.info("sort proccess | result: fail")
        raise RuntimeError("Error in sort process")
