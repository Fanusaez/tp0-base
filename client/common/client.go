package common

import (
	"net"
	"time"
	"os/signal"
	"os"
	"syscall"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Bet info
type Bet struct {
	Id string
	Nombre string
	Apellido string
	Documento string
	Nacimiento string
	Numero string
} 

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	bet Bet
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, bet Bet) *Client {
	client := &Client{
		config: config,
		bet: bet,
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

	for i := 0; i < c.config.LoopAmount; i++ {
		c.createClientSocket()

		// Serialize the bet
		var data []byte = serialiceBet(c.bet)
		
		// Send the bet
		err := c.sendAll(data)
		if err != nil {
			log.Errorf("action: send_message | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
			return
		}

		// Receive ACK from server (4 bytes "ACK\n")  
		c.reciveAck()

		// Close the connection
		c.conn.Close()
		
		// Log the success
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
			c.bet.Documento,
			c.bet.Numero,
		)
	}
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

func (c* Client) reciveAck() {
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
