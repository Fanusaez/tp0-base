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

---

## Parte 2

### Ejercicio 5

**Protocolo para enviar apuesta (Bet):**

- Por cada campo:
  - 2 bytes con la longitud del campo (Big Endian).
  - Campo serializado (en UTF-8).

**Del lado del servidor**, esta información se deserializa campo a campo para construir una instancia de `Bet`.

### Ejercicio 6

__Protocolo utilizado para la serializacion de batches__:

- Cliente: 
    * 2 bytes para indicar la cantidad de bytes a leer (tamaño del batch)

    Y para cada bet del batch:
    * 2 bytes indicando el tamaño del campo a leer
    * Infomacion del campo (UTF-8)
    * Esto se repetia para cada campo (ID, Nombre, apellido, documento, numero)

- Servidor:
    * Deserealizada esta informaciion y la guardaba en una clase `Bet` (para cada Bet del batch)

Este protocolo fue levemente modificado para el ejercicio 7
