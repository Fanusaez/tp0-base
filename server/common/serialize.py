# Protocolo:
#   - 2 byte: cantidad de ganadores
#   - Por cada ganador:
#       - 2 byte: longitud del DNI
#       - DNI 

import logging

def send_winners(socket, winners_bet):
    """
    Send winners bets to client
    """
    response = b""
    logging.info("Cantidad de ganadores: " + str(len(winners_bet)))
    try:
        # Escribir la cantidad de ganadores (2 bytes)
        response += len(winners_bet).to_bytes(2, byteorder="big")

        for bet in winners_bet:
            dni_bytes = bet.document.encode("utf-8")
            response += len(dni_bytes).to_bytes(2, byteorder="big")  # tamaño del DNI
            response += dni_bytes  # el DNI como tal

        send_all(socket, response)

        logging.info(f"Winners sent to client")
    except RuntimeError as e:
        logging.error(f"Error sending winners, connection closed")

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