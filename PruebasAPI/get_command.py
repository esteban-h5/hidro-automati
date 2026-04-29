"""
Endpoint a utiliza:

GET api/v2/works/{workId}
GET api/v2/works/{workId}/Samples
POST api/v2/samples
POST api/v2/works
POST api/v2/samples/{sampleId}/Works/Attach/{workId}
POST api/v2/QCTests
"""

import requests
import keyring
import json
import sys
import argparse

DEFAULT_URL = "https://hidrolab.mylimsweb.cloud/api/v2/"
DEFAULT_ENDPOINT = ""
DEFAULT_TIMEOUT = 10.0

def parse_args():
    parser = argparse.ArgumentParser(description="Cliente API myLims rápido y sencillo.")
    
    parser.add_argument("-u", "--url", default=DEFAULT_URL, help=f"URL base de la API (Default: {DEFAULT_URL})")
    parser.add_argument("-e", "--endpoint", default=DEFAULT_ENDPOINT, help=f"Endpoint específico (Default: {DEFAULT_ENDPOINT})")
    parser.add_argument("-t", "--timeout", type=float, default=DEFAULT_TIMEOUT, help=f"Timeout en segundos (Default: {DEFAULT_TIMEOUT})")
    parser.add_argument("-p", action="store_true", help="Mostrar información completa (no elimina el campo 'Result')")
    
    return parser.parse_args()

# === FUNCIONES AUXILIARES ===
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def api_get(url_base, endpoint, timeout, token):
    url = f"{url_base}{endpoint}"
    eprint(f"--- Iniciando Solicitud ---")
    eprint(f"URL: {url} | Timeout: {timeout}s")
    
    try:
        out = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "x-access-key": token,
            },
            timeout=timeout
        )
        return out
    except requests.exceptions.Timeout:
        eprint("Error: La solicitud excedió el tiempo de espera.")
        sys.exit(1)
    except Exception as e:
        eprint(f"Error inesperado: {e}")
        sys.exit(1)

# === EJECUCIÓN ===
if __name__ == "__main__":
    args = parse_args()
    
    # 2. Obtener Token
    TOKEN = keyring.get_password("mylims_app", "secret7")
    if not TOKEN:
        eprint("Error: No se encontró el token en keyring.")
        sys.exit(1)

    # 3. Llamada a la API usando los argumentos indexados
    data_api = api_get(args.url, args.endpoint, args.timeout, TOKEN)

    if data_api.status_code == 200:
        data = data_api.json()

        # Si NO pasaste la bandera -p, ejecutamos la limpieza del Result
        if not args.p:
            if data and "Result" in data:
                del data["Result"]
        
        print(json.dumps(data, indent=4, ensure_ascii=False))
        
    else:
        eprint(f"Error de API ({data_api.status_code}): {data_api.text}")