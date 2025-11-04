import flask
import requests  
import time       
import random     
import logging  

app = flask.Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVICE_URLS = {
    "catalogo": "http://localhost:5001/api/producto/123", # 123 es un ID de ejemplo
    "pagos_transaccion": "http://localhost:5002/api/pagos/transaccion",
    "pagos_compensacion": "http://localhost:5002/api/pagos/compensacion",
    "inventario": "http://localhost:5003/api/inventario/actualizar",
    "compras_transaccion": "http://localhost:5004/api/compras/transaccion",
    "compras_compensacion": "http://localhost:5004/api/compras/compensacion",
}


def simular_latencia():
    """Simula un retraso de red, como pide el TP."""
    time.sleep(random.uniform(0.1, 0.5))

def compensar(servicios_a_compensar):
    """
    Ejecuta las compensaciones en orden inverso.
    """
    logging.warning(f"INICIANDO COMPENSACIÓN para: {servicios_a_compensar}")
    if "pagos" in servicios_a_compensar:
        try:
            logging.info("Compensando -> ms-pagos")
            simular_latencia()
            requests.post(SERVICE_URLS["pagos_compensacion"]) # Llama a la compensacion de pagos
            logging.info("Compensación de ms-pagos OK")
        except requests.RequestException as e:
            logging.error(f"FALLO CRÍTICO al compensar ms-pagos: {e}")
            
            
    if "compras" in servicios_a_compensar:
       
        try:
            logging.info("Compensando -> ms-compras")
            simular_latencia()
            requests.post(SERVICE_URLS["compras_compensacion"])
            logging.info("Compensación de ms-compras OK")
        except requests.RequestException as e:
            logging.error(f"FALLO CRÍTICO al compensar ms-compras: {e}")



@app.route('/api/compra', methods=['POST'])
def iniciar_compra():
    """
    Este es el endpoint principal que orquesta toda la transacción.
    """
    logging.info("--- 🚀 INICIANDO SAGA DE COMPRA ---")
    
    servicios_compensar = []
    
    try:
        #1)consulta catalogo (Paso de solo lectura, no requiere compensación)
        logging.info("Paso 1: Llamando a ms-catalogo...")
        simular_latencia()
        response_catalogo = requests.get(SERVICE_URLS["catalogo"])
        logging.info(f"ms-catalogo OK (Producto: {response_catalogo.json()})")

        #2)Realizar Pago (ms-pagos)
        logging.info("Paso 2: Llamando a ms-pagos (Transacción)...")
        servicios_compensar.append("pagos")
        simular_latencia()
        response_pagos = requests.post(SERVICE_URLS["pagos_transaccion"])
        
        #puede retornar 409
        if response_pagos.status_code != 200:
            logging.warning("ms-pagos RECHAZÓ la transacción (409)")
            raise Exception("Fallo en ms-pagos")

        logging.info("ms-pagos OK (Pago aceptado)")

        #3. Actualizar Inventario (ms-inventario)
        logging.info("Paso 3: Llamando a ms-inventario...")
        simular_latencia()
        response_inventario = requests.post(SERVICE_URLS["inventario"])
        
        #puede retornar 409 (sin stock)
        if response_inventario.status_code != 200:
            logging.warning("ms-inventario RECHAZÓ la actualización (409 - Sin Stock)")
            raise Exception("Fallo en ms-inventario (Sin Stock)")

        logging.info("ms-inventario OK (Stock actualizado)")

        #4)Guardar Compra (ms-compras)
        logging.info("Paso 4: Llamando a ms-compras (Transacción)...")
        servicios_compensar.append("compras")
        simular_latencia()
        response_compras = requests.post(SERVICE_URLS["compras_transaccion"])

        if response_compras.status_code != 200:
            logging.warning("ms-compras RECHAZÓ la transacción (409)")
            raise Exception("Fallo en ms-compras")

        logging.info("ms-compras OK (Compra guardada)")

        logging.info(" SAGA COMPLETADA CON ÉXITO ")
        return flask.jsonify({"mensaje": "¡Compra realizada con éxito!"}), 200

    except Exception as e:
        logging.error(f" FALLO EN LA SAGA: {e} ")
        
        compensar(servicios_compensar)
        
        return flask.jsonify({"mensaje": f"La transacción falló y fue revertida. Motivo: {e}"}), 409

if __name__ == '__main__':
    app.run(port=5000, debug=True)