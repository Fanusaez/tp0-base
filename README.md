# Trabajo Practico 0

**Alumno:** Edgardo Francisco Saez  
**Padrón:** 104896

---

## Parte 1

### Ejercicio 1

Se desarrolló el script `generar_compose.sh` que automatiza la generación del archivo `docker-compose-dev.yaml`.

**Ejecución:**

```bash
chmod +x generar_compose.sh
./generar_compose.sh <nombre_archivo_salida> <cantidad_clientes>
```

Este script ejecuta un programa en Python que escribe dinámicamente el archivo deseado.


### Ejercicio 2

Se configuró el `docker-compose-dev.yaml` para inyectar los archivos de configuración (como `config.yaml` o los datasets) mediante volúmenes, evitando así la reconstrucción de las imágenes en cada cambio.

### Ejercicio 3
Se provee el script `validar_echo_server.sh` para validar que el servidor echo funcione correctamente.

**Ejecución:**

```bash
chmod +x validar_echo_server.sh
./validar_echo_server.sh
```

Este script se ejecuta completamente dentro de la red virtual de Docker (`testing_net`) sin exponer puertos al host. Para ello, lanza un contenedor temporal (`busybox`) que usa netcat (`nc`) para enviar y recibir un mensaje.

### Ejercicio 4

**Servidor (Python):**

- Captura la señal `SIGTERM`.
- Llama a la función `shutdown()` para cerrar los sockets del cliente y servidor.
- Termina la ejecución con `sys.exit(0)`.

**Cliente (Go):**

- Se configura un canal para capturar señales del sistema.
- Se lanza una goroutine que maneja estas señales (`SIGTERM`, `SIGINT`).
- Cierra el socket con `Close()`, luego termina con `os.Exit(0)`.
