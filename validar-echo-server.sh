#!/bin/bash

# Obtener el nombre de la red desde docker-compose
NOMBRE_RED=$(docker network ls --format "{{.Name}}" | grep testing_net)
SERVER_NAME="server"
SERVER_PORT=$(grep 'SERVER_PORT' ./server/config.ini | cut -d '=' -f2 | tr -d ' ')
MENSAJE="TestMessage123"

# Verificar si la red existe
if [ -z "$NOMBRE_RED" ]; then
    echo "Error: La red de Docker 'testing_net' no está disponible."
    exit 1
fi

# Verificar si el puerto existe
if [ -z "$SERVER_PORT" ]; then
    echo "Error: El puerto del servidor no está disponible."
    exit 1
fi

# Ejecutar un contenedor temporal en la red de Docker para probar la conexión con netcat
RESPUESTA=$(docker run --rm --network "$NOMBRE_RED" busybox sh -c \
    "echo '$MENSAJE' | nc $SERVER_NAME $SERVER_PORT")

# Verificar si la respuesta es igual al mensaje enviado
if [ "$RESPUESTA" = "$MENSAJE" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi
