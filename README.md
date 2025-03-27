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
