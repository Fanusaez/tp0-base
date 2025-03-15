import socket
import logging


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
                self.client_socket = client_socket
                self.__handle_client_connection(self.client_socket)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            client_sock.send("{}\n".format(msg).encode('utf-8'))
            
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

    def shutdown(self):
        """
        Shutdown server socket

        Method to close server socket and client socket if posible
        """
        self.running = False
        try:
            if self.client_socket:
                self.client_socket.close()
            logging.info("action: shutdown | result: success")
        except OSError as e:
            logging.error(f"action: shutdown | result: fail | error: {e}")
        finally:
            self._server_socket.close()
            logging.info("Server has been shutdown")

        