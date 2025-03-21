package common

import (
	"bytes"
	"encoding/binary"
	"os"
	"bufio"
	"strings"
)

// Parse the CSV file and return batchSize bets or the number of bets
// that does not exceed 8000 bytes
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

	currentBatchBytes := ProtocolFieldLength // 2 bytes para indicar tamanio de cada batch
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
		betBytesSize := ProtocolFieldLength
		for _, field := range fields {
			betBytesSize += len(field)
		}

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

func serializeBatch(batch []Bet) []byte {
	buffer := new(bytes.Buffer)
	auxBuffer := new(bytes.Buffer)

	// Escribir un campo individual
	writeField := func(data string, buffer *bytes.Buffer) {
		binary.Write(buffer, binary.BigEndian, uint16(len(data)))
		buffer.WriteString(data)
	}

	for _, bet := range batch {
		betBuffer := new(bytes.Buffer)

		// Escribir cada campo en betBuffer
		writeField(bet.Id, betBuffer)
		writeField(bet.Nombre, betBuffer)
		writeField(bet.Apellido, betBuffer)
		writeField(bet.Documento, betBuffer)
		writeField(bet.Nacimiento, betBuffer)
		writeField(bet.Numero, betBuffer)

		betBytes := betBuffer.Bytes()

		// Escribir tamaño de la apuesta
		binary.Write(auxBuffer, binary.BigEndian, uint16(len(betBytes)))
		auxBuffer.Write(betBytes)
	}

	// Escribir tamaño del batch + contenido
	batchBytes := auxBuffer.Bytes()
	binary.Write(buffer, binary.BigEndian, uint16(len(batchBytes)))
	buffer.Write(batchBytes)

	return buffer.Bytes()
}