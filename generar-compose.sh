#!/bin/bash

# Verificar parámetros
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <archivo_salida> <cantidad_clientes>"
    exit 1
fi

ARCHIVO_SALIDA=$1
CANT_CLIENTES=$2

# Llamar al script en Python
python3 mi_generador.py "$ARCHIVO_SALIDA" "$CANT_CLIENTES"
