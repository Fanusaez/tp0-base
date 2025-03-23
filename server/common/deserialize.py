
from common.utils import *
import logging

def receive_batch(client_sock):
    """
    Recibe y deserializa un batch de apuestas desde un socket.
    Retorna:
      - lista de apuestas
      - bandera de éxito total (True) o parcial/incompleto (False)
    """
    bets = []
    success = True

    try:
        # Total bytes from the batch
        batch_size_raw = receive_all(client_sock, FIELD_LENGTH_BYTES)

        # No more batches, client may have sent all
        if not batch_size_raw or len(batch_size_raw) != FIELD_LENGTH_BYTES:
            return bets, success
        
        # If batch size is 0, client has no more batches
        if int.from_bytes(batch_size_raw, byteorder='big') == 0:
            return [], success
        
        batch_size = int.from_bytes(batch_size_raw, byteorder='big')
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

            bet = deserialize_bet(bet_raw)
            bets.append(bet)
            batch_size -= (FIELD_LENGTH_BYTES + bet_size)

    except RuntimeError as e:
        logging.error(f"Error general en receive_batch: {e}")
        success = False
        return bets, success

    return bets, success

def deserialize_bet(data):
    bet_fields = []
    index = 0
    for _ in range(6):  # Tenemos 6 campos en cada apuesta
        field_length = int.from_bytes(data[index:index+FIELD_LENGTH_BYTES], byteorder="big")
        index += 2
        field_value = data[index:index+field_length].decode("utf-8")
        index += field_length
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
    try:
        # Verificamos operacion
        operation = receive_all(client_sock, OPPERATION_FIELD_LENGTH)
        if not operation or len(operation) != OPPERATION_FIELD_LENGTH or int.from_bytes(operation, 'big') != REQUEST_WINNERS_AGENCY_ACTION:
            logging.error("Error al recibir operacion")
            return None
        
        # Recibimos longitud de bytes de id de agencia
        len_id_raw = receive_all(client_sock, FIELD_LENGTH_BYTES)
        if not len_id_raw or len(len_id_raw) != FIELD_LENGTH_BYTES:
            logging.error("Error al recibir la longitud del id de agencia")
            return None
        
        # Recibimos id de agencia
        id_agency_raw = receive_all(client_sock, int.from_bytes(len_id_raw, 'big'))
        if not id_agency_raw or len(id_agency_raw) != int.from_bytes(len_id_raw, 'big'):
            logging.error("Error al recibir id de agencia")
            return None
        
        # Retornamos id de agencia
        id_agencia = id_agency_raw.decode('utf-8')
        logging.info(f"Id de agencia recibido: {id_agencia}")
        return int(id_agencia)
    
    except RuntimeError as e:
        logging.error(f"Error general en receive_winners_request: {e}")
        return None
    
def handshake(socket):
    try:
        len_id_raw = receive_all(socket, FIELD_LENGTH_BYTES)
        if not len_id_raw or len(len_id_raw) != FIELD_LENGTH_BYTES:
            logging.error("Error en handshake al recibir la longitud del id de cliente")
            return None
        len_id = int.from_bytes(len_id_raw, 'big')

        id_raw = receive_all(socket, len_id)
        if not id_raw or len(id_raw) != len_id:
            logging.error("Error wn handshake al recibir el id de cliente")
            return None
        
        id = id_raw.decode('utf-8')
        logging.info(f"Handshake exitoso, id de cliente: {id}")
        return int(id)
    except:
        logging.error("Error en handshake")
        return None