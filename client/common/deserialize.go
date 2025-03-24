package common

import (
	"encoding/binary"
	"net"
)


// Prtocol
// - 2 bytes: amount of winners
// - 2 bytes: length of dni
// - n bytes: dni
func ReceiveWinners(socket net.Conn) ([]string, error) {
	// Recive the amount of winners
	amountWinnersRaw, err := ReciveAll(socket, 2)
	if err != nil {
		log.Errorf("Error al recibir la cantidad de ganadores: %v", err)
		return nil, err
	}
	// Convert the amount of winners to int
	amountWinners := binary.BigEndian.Uint16(amountWinnersRaw)

	winnersDni := make([]string, amountWinners)
	for i := 0; i < int(amountWinners); i++ {
		// Recive the winner
		winnerDniLenghtRaw, err := ReciveAll(socket, ProtocolFieldLength)
		if err != nil {
			log.Errorf("Error al recibir el ganador: %v", err)
			return nil, err
		}
		winnerDniLenght := binary.BigEndian.Uint16(winnerDniLenghtRaw)
		dni, _ := ReciveAll(socket, int(winnerDniLenght))
		winnersDni[i] = string(dni)
	}
	return winnersDni, nil
}

func ReceiveNumberOfWinners(socket net.Conn) (int, error) {
	// Recive the amount of winners
	amountWinnersRaw, err := ReciveAll(socket, 4)
	if err != nil {
		log.Errorf("Error al recibir la cantidad de ganadores: %v", err)
		return 0, err
	}
	// Convert the amount of winners to int
	amountWinners := binary.BigEndian.Uint32(amountWinnersRaw)
	return int(amountWinners), nil
}