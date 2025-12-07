#  Sistema de Comercio Electrónico con Patrón Saga (Orquestación)

Este es el proyecto para la materia, donde resolvemos el problema de mantener los datos coherentes (ACID) usando microservicios. Para lograrlo, usé el **Patrón Saga** controlado por un **Orquestador**.
##  Descripción del Proyecto

El sistema simula una compra online usando 5 microservicios separados. El "Orquestador" es el que dirige todo: va llamando a los otros servicios paso a paso.

##  Guía de Instalación y Despliegue

Como el TP está dividido en varios repositorios (cada servicio tiene el suyo), hay que seguir estos pasos para bajar todo y ejecutarlo junto.

### Paso 1: Crear la carpeta principal
Crea una carpeta en tu equipo llamada `tp-saga`. Esta será la raíz del proyecto.

```bash
mkdir tp-saga
cd tp-saga
```
### Paso 2: Dentro de la carpeta clonar este Orquestador y los 4 microservicios a continuacion

```bash
https://github.com/Salinas5/ms-catalogo.git
```

```bash
https://github.com/Salinas5/ms-inventario.git
```

```bash
https://github.com/Salinas5/ms-pagos.git
```

```bash
https://github.com/Salinas5/ms-compras.git
```
### Paso 3: Crear dentro de la carpeta este docker-compose.yml

```bash
version: '3.8'

services:
  ms-orquestador:
    build: ./ms-orquestador
    ports:
      - "5000:5000"
    depends_on:
      - ms-catalogo
      - ms-pagos
      - ms-inventario
      - ms-compras

  ms-catalogo:
    build: ./ms-catalogo
    ports:
      - "5001:5001"

  ms-pagos:
    build: ./ms-pagos
    ports:
      - "5002:5002"

  ms-inventario:
    build: ./ms-inventario
    ports:
      - "5003:5003"

  ms-compras:
    build: ./ms-compras
    ports:
      - "5004:5004"
```
### Paso 4: Ejecucion del proyecto
Una vez hecho los pasos anteriores coloca este comando 
```bash
docker-compose up --build
```
Esto comenlzara os 5 contenedores y creara una red interna para que se comuniquen entre ellos

El punto de entrada es el Orquestador en el puerto 5000.

Puedes utilizar Postman, Thunder Client o curl para realizar una compra.

Endpoint: POST http://localhost:5000/api/compra

Escenarios Posibles:
 Éxito : Todos los servicios responden OK.

Status: 200 OK

Respuesta: {"mensaje": "¡Compra realizada con éxito!"}

 Fallo y Compensación: Algún servicio falla (ej. sin stock) y el orquestador revierte la transacción.

Status: 409 CONFLICT

Respuesta: {"mensaje": "La transacción falló y fue revertida. Motivo: ..."}

### Tecnologias utilizadaS
Docker
Python
Flask

## Autores

- [@agustin_salinas](https://github.com/Salinas5)
- [@juliana_bustos](https://github.com/bustosjuliana)


