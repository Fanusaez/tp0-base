package common

import (
	"bufio"
	"bytes"
	"encoding/binary"
	"net"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID             string
	ServerAddress  string
	LoopAmount     int
	LoopPeriod     time.Duration
	BatchMaxAmount int
}

// Bet info
type Bet struct {
	Id         string
	Nombre     string
	Apellido   string
	Documento  string
	Nacimiento string
	Numero     string
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {

	// Capturar SIGTERM
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM)

	// Goroutine para manejar SIGTERM
	go func() {
		<-sigChan
		log.Infof("Recibido SIGTERM. Cerrando cliente de manera controlada...")
		c.Close()
		close(sigChan)
		os.Exit(0)
	}()

	var all_batches [][]Bet = ReadBetsFromCSV("/data/agency.csv", c.config.BatchMaxAmount, c.config.ID)

	c.createClientSocket()

	for i := 0; i < len(all_batches); i++ {

		// Serialize the bet
		var data_of_batch []byte = serializeBatch(all_batches[i])

		// Send the bet
		err := c.sendAll(data_of_batch)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}
	}

	// Receive ACK from server (4 bytes "ACK\n")
	c.reciveAck()

	// Close the connection
	c.conn.Close()
}

func serializeBatch(batch []Bet) []byte {
	buffer := new(bytes.Buffer)
	auxBuffer := new(bytes.Buffer)

	// Escribir un campo individual
	writeField := func(data string, buffer *bytes.Buffer) {
		binary.Write(buffer, binary.BigEndian, uint16(len(data))) // ✅ Escribir en el buffer recibido
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

	currentBatchBytes := 2 // 2 bytes para indicar tamanio de cada batch
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
		betBytesSize := 2
		for _, field := range fields {
			betBytesSize += len(field)
		}

		betBytesSize += 12 // 6 fields * 2 bytes

		if currentBatchBytes+betBytesSize < 8000 && len(currentBatch) < batchSize {
			// 12 bytes (2 bytes para indicar tamanio de cada campo)
			// TODO: HACER CONSTANTES DESCRIPTVAS
			currentBatchBytes += betBytesSize
			currentBatch = append(currentBatch, bet)
		} else {
			all_batches = append(all_batches, currentBatch)
			currentBatch = []Bet{bet}
			// 2 bytes(indican tamanio de cada batch)
			// 2 bytes (indican tamanio del Bet)
			currentBatchBytes = betBytesSize + 2
		}
	}
	return all_batches
}

// Sends a message to the server
func (c *Client) sendAll(data []byte) error {
	totalSent := 0
	for totalSent < len(data) {
		sent, err := c.conn.Write(data[totalSent:])
		if err != nil {
			log.Errorf("Error al enviar la apuesta: %v", err)
			return err
		}
		totalSent += sent
	}
	return nil
}

// Recive lenData bytes from the server
func (c *Client) reciveAll(lenData int) ([]byte, error) {
	buffer := make([]byte, lenData)
	totalReceived := 0

	for totalReceived < lenData {
		n, err := c.conn.Read(buffer[totalReceived:])
		if err != nil {
			log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return nil, err
		}
		totalReceived += n
	}

	return buffer, nil
}

func (c *Client) reciveAck() {
	// Receive ACK from server (4 bytes "ACK\n")
	ack, err := c.reciveAll(4)
	if err != nil {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
		return
	}

	if string(ack) != "ACK\n" {
		log.Errorf("action: receive_message | result: fail | client_id: %v | error: invalid ack",
			c.config.ID,
		)
		return
	}
}

// Close cierra la conexión del cliente de forma segura
func (c *Client) Close() {
	if c.conn != nil {
		log.Infof("Cerrando conexión del cliente...")
		c.conn.Close()
		c.conn = nil
	}
}
