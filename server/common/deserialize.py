
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
    index = 0
    success = True

    try:
        # Leer tamaño del batch (2 bytes)
        batch_size_raw = recive_all(client_sock, 2)
        if not batch_size_raw or len(batch_size_raw) != 2:
            # True dado que seguro no tiene mas batchs para leer.
            return None, True

        batch_size = int.from_bytes(batch_size_raw, byteorder='big')

        # Leer hasta batch_size bytes, o lo que se pueda (por si se corta)
        batch_data = b""
        while len(batch_data) < batch_size:
            # Cambiar despues
            chunk = client_sock.recv(batch_size - len(batch_data))
            if not chunk:
                return bets, False
            batch_data += chunk

        # Leer apuestas una por una
        while index < len(batch_data):
            # Verificar si hay 2 bytes para el tamaño de la apuesta
            if index + 2 > len(batch_data):
                logging.warning("Batch truncado: no hay tamaño de apuesta.")
                success = False
                break

            bet_size = int.from_bytes(batch_data[index:index+2], byteorder="big")
            index += 2

            # Verificar si hay datos suficientes para la apuesta
            if index + bet_size > len(batch_data):
                logging.warning("Apuesta incompleta en batch.")
                success = False
                break

            bet_raw = batch_data[index:index+bet_size]
            index += bet_size

            try:
                bet = deserialize_bet(bet_raw)
                bets.append(bet)
            except Exception as e:
                logging.error(f"Error deserializando apuesta: {e}")
                success = False
                break

    except Exception as e:
        logging.error(f"Error general en receive_batch: {e}")
        return bets, False

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

def recive_all(client_socket, bytes_to_receive):
        """Reads exactly bytes_to_receive bytes from client_socket"""
        data = b""
        while len(data) < bytes_to_receive:
            packet = client_socket.recv(bytes_to_receive - len(data))
            if not packet:
                # Client close the connection, no more batchs
                return None
            data += packet
        return data
