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

### Ejercicio 7

 Protocolos Cliente: 

- __Para el envio de los batches:__

    * 2 bytes para indicar la cantidad de bytes a leer (tamaño del batch)

    Y para cada bet del batch:
    * 2 bytes indicando el tamaño de la Bet correspondiente
    * 2 bytes indicando el tamaño del campo a leer
    * Infomacion del campo 
    * Esto se repetia para cada campo (ID, Nombre, apellido, documento, numero)

- __Para el envio del ACK:__

    * 4 bytes compuestos del string "ACK\n"

- __Para informar que se enviaron todos los batches:__
    * Entero de dos bytes con valor 0

- __Para para pedir los ganadores:__
    * 1 byte para indicar la instrucion
    * 2 bytes para indicar la longitud del campo ID 
    * n bytes para el campo id

Protocolos Servidor:

- __Para el envio de la cantidad de clientes que ganaron la apuesta__

    * 4 bytes (big endian)

- __Para enviar los documento de los ganadores__ 

    * 2 bytes indicando la cantidad de DNI's (big endian)
    * Para cada uno de los documentos:
    * 2 bytes indicando la cantidad de bytes que ocupa el DNI
    * n bytes del documento(UTF-8)

---