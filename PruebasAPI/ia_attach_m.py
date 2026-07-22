import sys
import json
import requests
import csv
import keyring

# === CONFIGURACIÓN API ===
API_URL = "https://hidrolab.mylimsweb.cloud/api/v2/"
TOKEN = keyring.get_password("mylims_app", "secret7")

# === FUNCIONES AUXILIARES ===
def eprint(*args, **kwargs):
    """Imprimir logs y errores en stderr."""
    print(*args, file=sys.stderr, **kwargs)


def api_post(endpoint: str, body: dict):
    """Enviar solicitud POST a la API."""
    url = f"{API_URL}{endpoint}"
    eprint(f"\n[POST] Solicitando a: {url}")
    
    try:
        out = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-access-key": TOKEN,
            },
            data=json.dumps(body),
        )
        eprint(f"Status Code: {out.status_code}")
        return out
    except Exception as e:
        eprint(f"Error en la solicitud: {e}")
        return None


# === PROCESAMIENTO DEL ARCHIVO CSV ===
NOMBRE_ARCHIVO = "muestras_con_coti_pe.csv"

try:
    # utf-8-sig evita que los títulos de las columnas se rompan si el CSV viene de Excel
    with open(NOMBRE_ARCHIVO, mode="r", encoding="utf-8-sig") as f:
        
        # OJO: Si tu CSV está separado por punto y coma (común en Excel en español), cambia a: delimiter=";"
        # Si está separado por tabulaciones (copiado y pegado), usa: delimiter="\t"
        reader = csv.DictReader(f, delimiter=",") 
        
        # Limpiar posibles espacios en blanco en los nombres de las columnas
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

        for row in reader:
            # Extraer y limpiar los IDs de la fila actual
            sample_id = row.get("ID MUESTRA", "").strip()
            coti_id = row.get("ID COTI", "").strip()
            pe_id = row.get("PE ID", "").strip()
            
            # Saltarse filas vacías o incompletas
            if not sample_id or not coti_id or not pe_id:
                eprint(f"Advertencia: Fila incompleta u omitida -> {row}")
                continue
            
            print(f"\n" + "="*50)
            print(f"PROCESANDO ID MUESTRA: {sample_id}")
            print(f"="*50)
            
            # 1. Primera solicitud: Attach ID COTI
            endpoint_coti = f"samples/{sample_id}/Works/Attach/{coti_id}"
            print(f"-> Adjuntando COTI ({coti_id})...")
            api_post(endpoint_coti, body={})
            
            # 2. Segunda solicitud: Attach PE ID
            endpoint_pe = f"samples/{sample_id}/Works/Attach/{pe_id}"
            print(f"-> Adjuntando PE ({pe_id})...")
            api_post(endpoint_pe, body={})

except FileNotFoundError:
    eprint(f"Error crítico: No se encontró el archivo '{NOMBRE_ARCHIVO}' en este directorio.")
    eprint("Asegúrate de ejecutar el script desde la misma carpeta donde está el CSV.")
except Exception as e:
    eprint(f"Ocurrió un error inesperado al procesar el archivo: {e}")

print("\n¡Proceso finalizado!")