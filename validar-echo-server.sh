#!/bin/bash

# Obtener el nombre de la red desde docker-compose
NOMBRE_RED=$(docker network ls --format "{{.Name}}" | grep testing_net)

# Verificar si la red existe
if [ -z "$NOMBRE_RED" ]; then
    echo "Error: La red de Docker 'testing_net' no está disponible."
    exit 1
fi

SERVER_NAME="server"
SERVER_PORT=12345
MENSAJE="TestMessage123"
TIEMPO_ESPERA=2

# Ejecutar un contenedor temporal en la red de Docker para probar la conexión con netcat
RESPUESTA=$(docker run --rm --network "$NOMBRE_RED" busybox sh -c \
    "echo '$MENSAJE' | nc -w $TIEMPO_ESPERA $SERVER_NAME $SERVER_PORT")

# Verificar si la respuesta es igual al mensaje enviado
if [ "$RESPUESTA" == "$MENSAJE" ]; then
    echo "action: test_echo_server | result: success"
    exit 0
else
    echo "action: test_echo_server | result: fail"
    exit 1
fi
