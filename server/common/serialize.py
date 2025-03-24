# Protocolo:
#   - 2 byte: cantidad de ganadores
#   - Por cada ganador:
#       - 2 byte: longitud del DNI
#       - DNI 

import logging

def send_winners(socket, winners_bet):
    """client_sock.close()client_sock.close()client_sock.close()client_sclient_sock.close()client_sock.close()ock.close().close()ock.close().close()ock.close()
    Send winners bets to client
    """
    response = b""
    try:
        # Escribir la cantidad de ganadores (2 bytes)
        response += len(winners_bet).to_bytes(2, byteorder="big")

        for bet in winners_bet:
            dni_bytes = bet.document.encode("utf-8")
            response += len(dni_bytes).to_bytes(2, byteorder="big")  # tamaño del DNI
            response += dni_bytes  # el DNI como tal

        send_all(socket, response)
    except RuntimeError as e:
        logging.error(f"Error sending winners, connection closed")
        raise e


# Protocolo:
#   -4 bytes: cantidad de ganadores
def send_number_of_winners(socket, number_of_winners):
    """
    Send number of winners to client
    """
    try:
        send_all(socket, number_of_winners.to_bytes(4, byteorder="big"))
    except:
        logging.error(f"Error sending number of winners")
        raise RuntimeError("Error sending number of winners")


def send_all(socket, data):
    """
    Send all data to client
    """
    try:
        total_sent = 0
        while total_sent < len(data):
            sent = socket.send(data[total_sent:])
            if sent == 0:
                return None
            total_sent += sent
    except:
        logging.error(f"Error sending winners")
        raise RuntimeError("Error sending winners")