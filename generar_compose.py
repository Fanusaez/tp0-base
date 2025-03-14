import sys

def generar_compose(archivo_salida, cantidad_clientes):
    with open(archivo_salida, "w") as f:
        f.write("name: tp0\n")
        f.write("services:\n")
        
        # Definir el servidor
        f.write("  server:\n")
        f.write("    container_name: server\n")
        f.write("    image: server:latest\n")
        f.write("    entrypoint: python3 /main.py\n")
        f.write("    volumes:\n")
        f.write("      - ./server/config.ini:/config.ini\n")
        f.write("    environment:\n")
        f.write("      - PYTHONUNBUFFERED=1\n")
        f.write("      - LOGGING_LEVEL=DEBUG\n")
        f.write("    networks:\n")
        f.write("      - testing_net\n\n")

        # Generar los clientes
        for i in range(1, int(cantidad_clientes) + 1):
            f.write(f"  client{i}:\n")
            f.write(f"    container_name: client{i}\n")
            f.write("    image: client:latest\n")
            f.write("    entrypoint: /client\n")
            f.write("    volumes:\n")
            f.write("      - ./client/config.yaml:/config.yaml\n")
            f.write("    environment:\n")
            f.write(f"      - CLI_ID={i}\n")
            f.write("      - CLI_LOG_LEVEL=DEBUG\n")
            f.write("    networks:\n")
            f.write("      - testing_net\n")
            f.write("    depends_on:\n")
            f.write("      - server\n\n")

        # Definir la red
        f.write("networks:\n")
        f.write("  testing_net:\n")
        f.write("    ipam:\n")
        f.write("      driver: default\n")
        f.write("      config:\n")
        f.write("        - subnet: 172.25.125.0/24\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 generar-compose.py <archivo_salida> <cantidad_clientes>")
        sys.exit(1)

    archivo_salida = sys.argv[1]
    cantidad_clientes = sys.argv[2]

    generar_compose(archivo_salida, cantidad_clientes)
