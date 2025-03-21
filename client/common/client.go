package common

import (
	"net"
	"os"
	"os/signal"
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
		err := SendAll(c.conn, data_of_batch)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		// Receive ACK from server (4 bytes "ACK\n")
		c.reciveAck()
	}

	// Close the connection
	c.conn.Close()
}

func (c *Client) reciveAck() {
	// Receive ACK from server (4 bytes "ACK\n")
	ack, err := ReciveAll(c.conn, AckSize)
	if err != nil {
		log.Errorf("action: receive_mess2age | result: fail | client_id: %v | error: %v",
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
