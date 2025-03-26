# Trabajo Practico 0

- Alumno: Edgardo Francisco Saez
- Padron: 104896

## Parte 1

### Ejercicio 1

Para este ejercicio creamos un docker-compose.sh

Para ejecutarlo:

```bash
./generar-compose.sh <nombre_archivo_salida> <cantidad_clientes>
```

Dentro del mismo se ejecuta un script de python que escribe el archivo especificado.

### Ejercicio 2

Inyecto en el archivo docker-compose-dev.yaml los archivos de configuracion para no tener que recontruir las imagenes de docker cada vez que se modifican los archivos

### Ejercicio 3
Para validar el correcto funcionamiento del servidor Echo, se provee un script de bash llamado validar_echo_server.sh.

Para ejecutarlo

```bash
./validar_echo_server.sh
```

Este test se ejecuta completamente dentro de la red virtual de Docker, sin exponer puertos al host. Para esto se lanza un contenedor temporal que utiliza la misma red que el servidor(testing_net) y se conecta usando netcat

### Ejercicio 4

- Server:
    Por el lado del server, lo que hacemos una vez catcheado el `SIGTERM` es:

    1 - Llamar a la funcion `shutdown()` la cual cierra los recursos que estan abiertos (sockets del cliente y servidor)

    2 - Llamar a `sys.exit(0)` el cual detiene la ejecucion del programa
    
- Client:

    1 - Creo un canal para poder recibir senales del sistema operativo

    2 - Congfiguro el canal para recibir senales como `syscall.SIGTERM`, `syscall.SIGINT`

    3 - Se inicia una goroutine para manejar las senales recibidas

    4 - Una vez se recibe, llamo a `Close()` (el cual cierra el socket del cliente), cierro el canal y realizo el `os.Exit(0)`

## Parte 2

### Ejercicio 5

Protocolo utilizado:

- Cliente:
    * 2 Bytes para indicar longitud del campo a recibir (bigendian)
    * Informacion del campo (string)
    * Esto se repetia para cada campo (ID, Nombre, apellido, documento, numero)

- Servidor:
    * Deserealizada esta informaciion y la guardaba en una clase `Bet`

### Ejercicio 6

Protocolo utilizado para la serializacion de batches:

- Cliente: 
    * 2 bytes para indicar la cantidad de bytes a leer (tamaño del batch)

    Y para cada bet del batch:
    * 2 bytes indicando el tamaño del campo a leer
    * Infomacion del campo 
    * Esto se repetia para cada campo (ID, Nombre, apellido, documento, numero)

- Servidor:
    * Deserealizada esta informaciion y la guardaba en una clase `Bet` (para cada Bet del batch)

Este protocolo fue levemente modificado para el ejercicio 7

### Ejercicio 7

 Cliente: 
    Para el envio de los batches


    * 2 bytes para indicar la cantidad de bytes a leer (tamaño del batch)

    Y para cada bet del batch:
    * 2 bytes indicando el tamaño de la Bet correspondiente
    * 2 bytes indicando el tamaño del campo a leer
    * Infomacion del campo 
    * Esto se repetia para cada campo (ID, Nombre, apellido, documento, numero)

    Para el envio del ACK

    * 4 bytes compuestos del string "ACK\n"

## Parte 4

### Ejercicio 8

