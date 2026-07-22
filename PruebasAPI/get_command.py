"""
Endpoint a utiliza:

GET api/v2/works/{workId}
GET api/v2/works/{workId}/Samples
POST api/v2/samples
POST api/v2/works
POST api/v2/samples/{sampleId}/Works/Attach/{workId}
POST api/v2/samples/24/Works/Attach/4496
POST api/v2/QCTests
"""

import requests
import keyring
import json
import sys
import argparse

# === CONFIGURACIÓN GLOBAL ===
API_URL = "https://hidrolab.mylimsweb.cloud/api/v2/"
DEFAULT_TIMEOUT = 10.0

# 1. Obtener Token desde el inicio para que sea accesible globalmente o por scope
TOKEN = keyring.get_password("mylims_app", "secret7")

def parse_args():
    parser = argparse.ArgumentParser(description="Cliente API myLims rápido y sencillo.")
    
    parser.add_argument("-e", "--endpoint", required=True, help="Endpoint específico (ej: works/123)")
    parser.add_argument("-m", "--method", choices=["GET", "POST"], default="GET", help="Método HTTP (Default: GET)")
    parser.add_argument("-d", "--data", help="JSON string para el body del POST")
    parser.add_argument("-t", "--timeout", type=float, default=DEFAULT_TIMEOUT, help="Timeout en segundos")
    parser.add_argument("-p", action="store_true", help="Mostrar información completa (no limpia 'Result')")
    
    return parser.parse_args()

def eprint(*args, **kwargs):
    """Imprimir en stderr para no ensuciar la salida JSON."""
    print(*args, file=sys.stderr, **kwargs)

# === TUS FUNCIONES REFACTORIZADAS ===

def api_get(endpoint: str):
    """Enviar solicitud GET a la API."""
    url = f"{API_URL}{endpoint}"
    eprint(f"--- Solicitando GET a: {url} ---")
    
    try:
        out = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "x-access-key": TOKEN,
            },
            timeout=DEFAULT_TIMEOUT
        )
        return out
    except Exception as e:
        eprint(f"Error en GET: {e}")
        sys.exit(1)

def api_post(endpoint: str, body: dict):
    """Enviar solicitud POST a la API."""
    url = f"{API_URL}{endpoint}"
    eprint(f"--- Solicitando POST a: {url} ---")
    
    try:
        out = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-access-key": TOKEN,
            },
            data=json.dumps(body),  # Asegura formato JSON correcto
            timeout=DEFAULT_TIMEOUT
        )
        eprint(f"POST Body => {json.dumps(body, indent=4, ensure_ascii=False)}")
        return out
    except Exception as e:
        eprint(f"Error en POST: {e}")
        sys.exit(1)

# === EJECUCIÓN ===
if __name__ == "__main__":
    if not TOKEN:
        eprint("Error: No se encontró el token en keyring.")
        sys.exit(1)

    args = parse_args()
    
    # Decidir qué función usar según el método
    if args.method == "GET":
        data_api = api_get(args.endpoint)
    else:
        # Para POST, parseamos el string data a un dict
        body_dict = {}
        if args.data:
            try:
                body_dict = json.loads(args.data)
            except json.JSONDecodeError:
                eprint("Error: El contenido de -d no es un JSON válido.")
                sys.exit(1)
        
        data_api = api_post(args.endpoint, body_dict)

    # Manejo de la respuesta
    if data_api.status_code in [200, 201]:
        try:
            res_json = data_api.json()

            # Limpieza opcional del campo 'Result' si no se usa -p
            if not args.p and isinstance(res_json, dict):
                if "Result" in res_json:
                    del res_json["Result"]
            
            print(json.dumps(res_json, indent=4, ensure_ascii=False))
        except ValueError:
            print(f"Éxito: {data_api.text}")
    else:
        eprint(f"Error de API ({data_api.status_code}): {data_api.text}")