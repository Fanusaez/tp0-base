package common

import (
	"encoding/binary"
	"net"
)



// Receive the winners from the server
// Protocol:
// 	- 2 bytes: amount of winners
// 	- 2 bytes: length of dni
// 	- n bytes: dni
func ReceiveWinners(socket net.Conn) ([]string, error) {
	// Recive the amount of winners
	amountWinnersRaw, err := ReciveAll(socket, 2)
	if err != nil {
		return nil, err
	}
	// Convert the amount of winners to int
	amountWinners := binary.BigEndian.Uint16(amountWinnersRaw)

	winnersDni := make([]string, amountWinners)
	for i := 0; i < int(amountWinners); i++ {
		// Recive the winner
		winnerDniLenghtRaw, err := ReciveAll(socket, ProtocolFieldLength)
		if err != nil {
			return nil, err
		}
		winnerDniLenght := binary.BigEndian.Uint16(winnerDniLenghtRaw)
		dni, _ := ReciveAll(socket, int(winnerDniLenght))
		winnersDni[i] = string(dni)
	}
	return winnersDni, nil
}

// Receive the amount of winners from the server
// Protocol:
// 	- 4 bytes: amount of winners
func ReceiveNumberOfWinners(socket net.Conn) (int, error) {
	// Recive the amount of winners
	amountWinnersRaw, err := ReciveAll(socket, 4)
	if err != nil {
		return 0, err
	}
	// Convert the amount of winners to int
	amountWinners := binary.BigEndian.Uint32(amountWinnersRaw)
	return int(amountWinners), nil
}

func ReciveAck(conn net.Conn) error {
	// Receive ACK from server (4 bytes "ACK\n")
	ack, err := ReciveAll(conn, AckSize)
	if err != nil {
		return err
	}

	if string(ack) != "ACK\n" {
		log.Errorf("action: receive_message | result: fail| error: invalid ack")
		return err
	}
	return nil
}