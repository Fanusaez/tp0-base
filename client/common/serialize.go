package common

import (
	"bytes"
	"encoding/binary"

)

// SerialiceBet Serializes a bet into a byte array
func serialiceBet(bet Bet) []byte {
	buffer := new(bytes.Buffer)

	// Aux function to write a field in the buffer
	writeField := func(data string) {
		if data == "" {
			data = " " // Avoid sending empty strings
		}
		// Write the length of the data (2 bytes representation)
		binary.Write(buffer, binary.BigEndian, uint16(len(data))) 
		// Write the data
		buffer.WriteString(data)                                 
	}

	// Write the fields
	writeField(bet.Id)
	writeField(bet.Nombre)
	writeField(bet.Apellido)
	writeField(bet.Documento)
	writeField(bet.Nacimiento)
	writeField(bet.Numero)

	return buffer.Bytes()
}
