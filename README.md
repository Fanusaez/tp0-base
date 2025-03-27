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