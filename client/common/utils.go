package common

import (
	"net"
	"bytes"
	"encoding/binary"
)

const ProtocolFieldLength = 2
const AllBetProtocolFieldsLength = 12 // Id + nombre + apellido + doc + nacimiento + nuemero
const MaxBytesBatch = 8000 // 8kb
const AckSize = 4

const AskForWinnerInstruction = 0x03

// Sends a message to the server
func SendAll(socket net.Conn, data []byte) error {
	totalSent := 0
	for totalSent < len(data) {
		sent, err := socket.Write(data[totalSent:])
		if err != nil {
			log.Errorf("Error al enviar la apuesta: %v", err)
			return err
		}
		totalSent += sent
	}
	return nil
}

// Recive lenData bytes from the server
func ReciveAll(socket net.Conn, lenData int) ([]byte, error) {
	buffer := make([]byte, lenData)
	totalReceived := 0

	for totalReceived < lenData {
		n, err := socket.Read(buffer[totalReceived:])
		if err != nil {
			log.Errorf("action: receive_message | result: fail | error: %v",
				err,
			)
			return nil, err
		}
		totalReceived += n
	}

	return buffer, nil
}


// Protocol:
// 1 byte: instrucción
// 2 bytes: longitud del campo de datos
// n bytes: datos
func AskForWinner(socket net.Conn, id string) {
	buf := new(bytes.Buffer)

	// Instrucción: 0x03
	buf.WriteByte(AskForWinnerInstruction)

	// Longitud de ID (2 bytes)
	binary.Write(buf, binary.BigEndian, uint16(len(id)))

	// ID como string (n bytes)
	buf.WriteString(id)

	// Enviar
	SendAll(socket, buf.Bytes())
}


// Protocol:
// 2 bytes longitud ID
// n bytes ID
func Handshake(socket net.Conn, id string) {
	buf := new(bytes.Buffer)

	// Longitud de ID (2 bytes)
	binary.Write(buf, binary.BigEndian, uint16(len(id)))

	// ID como string (n bytes)
	buf.WriteString(id)

	// Enviar
	SendAll(socket, buf.Bytes())
}