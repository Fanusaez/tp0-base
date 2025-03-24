#!/usr/bin/env python3

from configparser import ConfigParser
from common.server import Server
import logging
import os
import sys
import signal
from functools import partial


def handle_sigterm(server_instance, signum, frame):
    logging.info("Recibido SIGTERM. Cerrando servidor de manera controlada...")
    server_instance.shutdown()  # Método para cerrar conexiones y liberar recursos
    sys.exit(0)


def initialize_config():
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file. 
    If at least one of the config parameters is not found a KeyError exception 
    is thrown. If a parameter could not be parsed, a ValueError is thrown. 
    If parsing succeeded, the function returns a ConfigParser object 
    with config parameters
    """

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["port"] = int(config["DEFAULT"].get("SERVER_PORT", os.getenv('SERVER_PORT')))
        config_params["listen_backlog"] = int(config["DEFAULT"].get("SERVER_LISTEN_BACKLOG", os.getenv('SERVER_LISTEN_BACKLOG')))
        config_params["logging_level"] = config["DEFAULT"].get("LOGGING_LEVEL", os.getenv('LOGGING_LEVEL'))
        config_params["cant_clientes"] = int(config["DEFAULT"].get("CANT_CLIENTES", os.getenv('CANT_CLIENTES')))

    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params


def main():
    config_params = initialize_config()
    logging_level = config_params["logging_level"]
    port = config_params["port"]
    listen_backlog = config_params["listen_backlog"]
    cant_clientes = config_params["cant_clientes"]

    initialize_log(logging_level)

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug(f"action: config | result: success | port: {port} | "
                  f"listen_backlog: {listen_backlog} | logging_level: {logging_level} |  cant_clientes: {cant_clientes}")

    # Initialize server and start server loop
    server = Server(port, listen_backlog, cant_clientes)

    # Pasar el server a la función usando functools.partial
    signal.signal(signal.SIGTERM, partial(handle_sigterm, server))
    
    server.run()

def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()
