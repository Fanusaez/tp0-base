package common

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"net"
	"os"
	"strings"
)

// Bet 
type Bet struct {
	Id         string
	Nombre     string
	Apellido   string
	Documento  string
	Nacimiento string
	Numero     string
}



// Parse the CSV file and return a slice of batchs of bets
// Each batch contains a slice of bets that does not exceed 8000 bytes
// Protocol:
// 	- 2 bytes: size of the batch (only 1 time)
//	- 2 bytes: size of the bet	(each bet)
//  - 2 bytes: size of the field (each field)
//  - n bytes: field (each field)
func ReadBetsFromCSV(filePath string, batchSize int, agencyId string) [][]Bet {
	file, err := os.Open(filePath)

	if err != nil {
		log.Fatalf("Error al abrir el archivo: %v", err)
	}

	// Close when done
	defer file.Close()

	// all bets contains all the bets segmented into batchs
	all_batches := [][]Bet{}
	scanner := bufio.NewScanner(file)
	
	// The first 2 bytes are for the size of the batch
	currentBatchBytes := ProtocolFieldLength
	currentBatch := []Bet{}
	for scanner.Scan() {
		line := scanner.Text()
		fields := strings.Split(line, ",")

		// Create a bet
		bet := Bet{
			Id:         agencyId,
			Nombre:     fields[0],
			Apellido:   fields[1],
			Documento:  fields[2],
			Nacimiento: fields[3],
			Numero:     fields[4],
		}

		// Calculate the size (bytes) of the bet

		// 2 bytes to indicate total bytes of the bet
		betBytesSize := ProtocolFieldLength
		// Len of each field
		for _, field := range fields {
			betBytesSize += len(field)
		}
		// Bytes for each field lenght
		betBytesSize += AllBetProtocolFieldsLength // 6 fields * 2 bytes

		if currentBatchBytes+betBytesSize < MaxBytesBatch && len(currentBatch) < batchSize {
			currentBatchBytes += betBytesSize
			currentBatch = append(currentBatch, bet)
		} else {
			all_batches = append(all_batches, currentBatch)
			currentBatch = []Bet{bet}
			currentBatchBytes = betBytesSize + ProtocolFieldLength
		}
	}
	if len(currentBatch) > 0 {
		all_batches = append(all_batches, currentBatch)
	}
	return all_batches
}

// Protocol:
// 	- 2 bytes: size of the batch (only 1 time)
//	- 2 bytes: size of the bet	(each bet)
//  - 2 bytes: size of the field (each field)
//  - n bytes: field (each field)
func serializeBatch(batch []Bet) []byte {
	// Buffer to store the serialized batch
	buffer := new(bytes.Buffer)
	// Buffer to store the serialized bets
	auxBuffer := new(bytes.Buffer)

	// Function to write the length and field in the buffer
	writeField := func(data string, buffer *bytes.Buffer) {
		// Length of the field
		binary.Write(buffer, binary.BigEndian, uint16(len(data)))
		// Field
		buffer.WriteString(data)
	}

	for _, bet := range batch {
		betBuffer := new(bytes.Buffer)
		writeField(bet.Id, betBuffer)
		writeField(bet.Nombre, betBuffer)
		writeField(bet.Apellido, betBuffer)
		writeField(bet.Documento, betBuffer)
		writeField(bet.Nacimiento, betBuffer)
		writeField(bet.Numero, betBuffer)

		betBytes := betBuffer.Bytes()

		// Write the length of the bet and the bet in auxBuffer
		binary.Write(auxBuffer, binary.BigEndian, uint16(len(betBytes)))
		auxBuffer.Write(betBytes)
	}

	// Write the length of the batch and the batch in buffer
	batchBytes := auxBuffer.Bytes()
	binary.Write(buffer, binary.BigEndian, uint16(len(batchBytes)))
	buffer.Write(batchBytes)

	return buffer.Bytes()
}

func SendAck(conn net.Conn) error {
	// Send ACK to client (4 bytes "ACK\n")
	err := SendAll(conn, []byte("ACK\n"))
	if err != nil {
		log.Errorf("action: send_message | result: fail | error: %v",
			err,
		)
		return err
	}
	return nil
}