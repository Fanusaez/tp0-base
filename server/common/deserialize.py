
from common.utils import *
from common.constants import *
import logging

def receive_batch(client_sock):
    """
    Receives a batch of bets from a client socket. And it returns:
      - list of bets
      - success: True if batch was received successfully, False otherwise
    """
    bets = []
    success = True

    try:
        # Total bytes from the batch
        batch_size_raw = receive_all(client_sock, FIELD_LENGTH_BYTES)

        # No more batches, client may have sent all
        if not batch_size_raw or len(batch_size_raw) != FIELD_LENGTH_BYTES:
            return bets, success
        
        # Numbers of bytes in the batch
        batch_size = int.from_bytes(batch_size_raw, byteorder='big')

        # If batch size is 0, client has no more batches
        if batch_size == NO_MORE_BATCHES:
            return [], success
        
        while batch_size > 0:

            bet_size_raw = receive_all(client_sock, FIELD_LENGTH_BYTES)
            if not bet_size_raw or len(bet_size_raw) != FIELD_LENGTH_BYTES:
                success = False
                return bets, success
            
            bet_size = int.from_bytes(bet_size_raw, byteorder='big')

            bet_raw = receive_all(client_sock, bet_size)
            if not bet_raw or len(bet_raw) != bet_size:
                success = False
                return bets, success

            # Deserialize bet
            bet = deserialize_bet(bet_raw)
            # Append bet to list
            bets.append(bet)
            # Decrease batch size remaining
            batch_size -= (FIELD_LENGTH_BYTES + bet_size)

    except RuntimeError as e:
        logging.error(f"Error receiving or processing the batch: {e}")
        success = False
        return bets, success

    return bets, success

def deserialize_bet(data):
    """Deserializes a bet from a byte array and returns a Bet object."""

    bet_fields = []
    index = 0
    for _ in range(NUMBER_BET_ATTRIBUTES):
        # Read field length
        field_length = int.from_bytes(data[index:index+FIELD_LENGTH_BYTES], byteorder="big")
        index += 2
        # Read field value
        field_value = data[index:index+field_length].decode("utf-8")
        index += field_length
        # Append field value to bet_fields
        bet_fields.append(field_value)
    
    bet = Bet(*bet_fields)
    return bet

def receive_all(client_socket, bytes_to_receive):
    """Reads exactly bytes_to_receive bytes from client_socket."""
    data = b""
    while len(data) < bytes_to_receive:
        try:
            packet = client_socket.recv(bytes_to_receive - len(data))
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            raise RuntimeError("Error de red al recibir datos") from e

        if not packet:
            return None  # Cliente cerró conexión normalmente
        data += packet
    return data

def receive_winners_request(client_sock):
    """Recives a request from client to inform winners and returns the agency id"""
    try:
        # Verify operation
        operation = receive_all(client_sock, OPPERATION_FIELD_LENGTH)
        if not operation or len(operation) != OPPERATION_FIELD_LENGTH or int.from_bytes(operation, 'big') != REQUEST_WINNERS_AGENCY_ACTION:
            logging.error("Error receiving operation")
            return None
        
        # Receive agency id length
        len_id_raw = receive_all(client_sock, FIELD_LENGTH_BYTES)
        if not len_id_raw or len(len_id_raw) != FIELD_LENGTH_BYTES:
            logging.error("Error al recibir la longitud del id de agencia")
            return None
        
        # Process agency id
        id_agency_raw = receive_all(client_sock, int.from_bytes(len_id_raw, 'big'))
        if not id_agency_raw or len(id_agency_raw) != int.from_bytes(len_id_raw, 'big'):
            logging.error("Error receiving agency id")
            return None
        
        # Retornamos id de agencia
        id_agency = id_agency_raw.decode('utf-8')
        return int(id_agency)
    
    except RuntimeError as e:
        logging.error(f"Error receiving winners request: {e}")
        raise e
    
def handshake(socket):
    """ Handshake with client to receive client id"""
    try:
        len_id_raw = receive_all(socket, FIELD_LENGTH_BYTES)
        if not len_id_raw or len(len_id_raw) != FIELD_LENGTH_BYTES:
            logging.error("Error receiving client id length")
            return None
        len_id = int.from_bytes(len_id_raw, 'big')

        # Process id client
        id_raw = receive_all(socket, len_id)
        if not id_raw or len(id_raw) != len_id:
            logging.error("Error receiving client id")
            return None
        id = id_raw.decode('utf-8')
        # return client id as int
        return int(id)
    except:
        logging.error("Error in handshake")
        raise RuntimeError("Error in handshake")
    
def receive_ack(socket):
    """ Receive ACK from client"""
    try:
        ack_raw = receive_all(socket, ACK_LENGTH)
        if not ack_raw or len(ack_raw) != ACK_LENGTH:
            logging.error("Error receiving ACK")
            return False
        return ack_raw.decode('utf-8') == "ACK\n"
    except:
        logging.error("Error receiving ACK")
        raise RuntimeError("Error  receiving ACK")