# Verificar parámetros
if [ "$#" -ne 2 ]; then
    echo "Uso: $0 <archivo_salida> <cantidad_clientes>"
    exit 1
fi

ARCHIVO_SALIDA=$1
CANT_CLIENTES=$2

echo "Generando $ARCHIVO_SALIDA con $CANT_CLIENTES clientes..."

# Llamar al script en Python
python3 generar-compose.py "$ARCHIVO_SALIDA" "$CANT_CLIENTES"

echo "Generación completa."