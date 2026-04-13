import requests
import keyring
import json
import sys

# === CONFIGURACIÓN POR DEFECTO ===
DEFAULT_URL = "https://hidrolab.mylimsweb.cloud/api/"
DEFAULT_ENDPOINT = "Samples/2071546"
DEFAULT_TIMEOUT = 10.0  # Segundos

# === LÓGICA DE ARGUMENTOS (sys.argv) ===
# Si el usuario pasa argumentos, sobrescribimos los valores por defecto.
# sys.argv[0] siempre es el nombre del script.

argc = len(sys.argv)
API_URL = sys.argv[1] if argc > 1 else DEFAULT_URL
ENDPOINT = sys.argv[2] if argc > 2 else DEFAULT_ENDPOINT

try:
    TIMEOUT = float(sys.argv[3]) if argc > 3 else DEFAULT_TIMEOUT
except ValueError:
    print(f"[!] Error: El timeout debe ser numérico. Usando default: {DEFAULT_TIMEOUT}s", file=sys.stderr)
    TIMEOUT = DEFAULT_TIMEOUT

TOKEN = keyring.get_password("mylims_app", "secret7")

# === FUNCIONES AUXILIARES ===
def eprint(*args, **kwargs):
    """Imprimir logs técnicos en stderr para no ensuciar la salida de datos."""
    print(*args, file=sys.stderr, **kwargs)

def api_get(endpoint: str, timeout: float):
    """Enviar solicitud GET a la API."""
    url = f"{API_URL}{endpoint}"
    eprint(f"--- Iniciando Solicitud ---")
    eprint(f"URL: {url}")
    eprint(f"Timeout: {timeout}s")
    
    try:
        out = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "x-access-key": TOKEN,
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
data_api = api_get(ENDPOINT, TIMEOUT)

if data_api.status_code == 200:
    data = data_api.json()
    
    # Lógica de limpieza original
    if "Result" in data:
        del data["Result"]
    
    # Imprimir el JSON final en la consola (stdout)
    print(json.dumps(data, indent=4, ensure_ascii=False))
else:
    eprint(f"Error de API ({data_api.status_code}): {data_api.text}")