
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
        batch_size_raw = receive_all(client_sock, 2)

        # No more batches, client may have sent all
        if not batch_size_raw or len(batch_size_raw) != 2:
            return bets, success
        
        batch_size = int.from_bytes(batch_size_raw, byteorder='big')
        while batch_size > 0:

            bet_size_raw = receive_all(client_sock, 2)
            if not bet_size_raw or len(bet_size_raw) != 2:
                success = False
                return bets, success
            
            bet_size = int.from_bytes(bet_size_raw, byteorder='big')

            bet_raw = receive_all(client_sock, bet_size)
            if not bet_raw or len(bet_raw) != bet_size:
                success = False
                return bets, success

            bet = deserialize_bet(bet_raw)
            bets.append(bet)
            batch_size -= (2 + bet_size)

    except RuntimeError as e:
        logging.error(f"Error general en receive_batch: {e}")
        success = False
        return bets, success

    return bets, success

def deserialize_bet(data):
    bet_fields = []
    index = 0
    for _ in range(6):  # Tenemos 6 campos en cada apuesta
        field_length = int.from_bytes(data[index:index+2], byteorder="big")
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
