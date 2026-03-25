import requests
import keyring
import json
import sys
import os

# === CONFIGURACIÓN ===
API_URL = "https://hidrolab.mylimsweb.cloud/api/v2/"
TOKEN = keyring.get_password("mylims_app", "secret7")


# === FUNCIONES AUXILIARES ===
def eprint(*args, **kwargs):
    """Imprimir errores en stderr."""
    print(*args, file=sys.stderr, **kwargs)


def api_get(endpoint: str):
    """Enviar solicitud GET a la API."""
    url = f"{API_URL}{endpoint}"
    
    eprint(f"Solicitando a:\n {url}")
    out = requests.get(
        url,
        headers={
            "Content-Type": "application/json",
            "x-access-key": TOKEN,
        },
    )
    return out


def api_post(endpoint: str, body: dict):
    """Enviar solicitud POST a la API."""
    url = f"{API_URL}{endpoint}"
    eprint(f"Solicitando a:\n {url}")
    
    out = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "x-access-key": TOKEN,
        },
        data=json.dumps(body),  # Asegura formato JSON correcto
    )
    eprint(f"POST Body => {json.dumps(body, indent=4, ensure_ascii=False)}")
    return out


# === PROCESAMIENTO ===
# data_api = api_get("SampleTypes/1862")
# data_api = api_get("Samples/2071546")

# data_api = api_get("Accounts/2175")
# data_api = api_get("Accounts?$filter=Identification eq 'SOCIEDAD ADL DIAGNOSTIC CHILE SPA (PUERTO AYSEN)'")
# data_api = api_get("SampleTypes?$filter=Identification eq 'Agua Residual (P)'")


# data_api = api_get("Specifications?$filter=Identification eq 'DS 90 Tabla 1' and Active eq true")
# data_api = api_get("Samples?$filter=Account/Identification eq 'GSI INGENIEROS CONSULTORES LTDA'")
# data_api = api_get("samples/2094446/infos")
"""
#FILTRO HIDROLAB SCL FINALIZADAS
data_api = api_get("Samples?$filter=Account ne null and Active eq true and endswith(ControlNumber, '.0') and "+
                   "CurrentStatus/SampleStatus/Identification eq 'Finalizada' and "+
                   "ServiceCenter/Identification eq 'Hidrolab SCL'&$inlinecount=allpages")
                   
"""

#Samples?$filter=Account ne null and Active eq true and endswith(ControlNumber, '.0') and CurrentStatus/SampleStatus/Identification eq 'Finalizada' and ServiceCenter/Identification eq 'Hidrolab SCL'&$inlinecount=allpages

# data_api = api_get("Samples?$filter=Account/Identification eq 'Aquagestion S.A - Puerto Varas'&$inlinecount=allpages")#")+

# data_api = api_get("Samples?$filter=CurrentStatus/SampleStatus/Id eq 8")

#Muestras en estado recibida o analisis 

# data_api = api_get("samplereasons?$filter=Identification eq 'Rutina' and Active eq true")
#data_api = api_get("Methods?$top=200&$filter=LastVersion eq true and Active eq true and MethodType/Identification eq 'General'&$inlinecount=allpages")
# data_api = api_get("Methods/Analyses?$inlinecount=allpages&$filter=Method/Active eq true and Method/MethodType/Identification eq 'General'")
# data_api = api_get("User?$filter=Identification eq ''")
data_api = api_get("Users?$filter=startswith(Email,'daq')")
# data_api = api_get("Methods?$inlinecount=allpages&$filter=Active eq conchetumare and MethodType/Identification eq 'General'")
#data_api = api_get("ServiceAreas?$top=200&$inlinecount=allpages&$filter=Active eq true")
# data_api = api_get("?$top=200&$inlinecount=allpages&$filter=Active eq true")
# data_api = api_get("Methods/6070")
# data_api = api_get("AnalysisGroups/7903/Analyses")


# data_api = api_get("Accounts?$filter=Identification eq ")
#data_api = api_get("login")

# from datetime import datetime, timedelta
# from time import sleep

# x = "2025-01-01"
# fecha_inicial = datetime.strptime(x, "%Y-%m-%d")

# for dias in range(0, 140, 7):

    # sleep(1)
    # fecha_ini = fecha_inicial + timedelta(days=dias)
    # fecha_fin = fecha_ini + timedelta(days=7)

    # data_api = api_get(
        # f"Samples?$filter="
        # f"ReceivedTime gt datetime'{fecha_ini.strftime('%Y-%m-%d')}T00:00:00Z' and "
        # f"ReceivedTime lt datetime'{fecha_fin.strftime('%Y-%m-%d')}T11:59:59Z' and "
        # f"Active eq true"
        # f"&$inlinecount=allpages"
    # )

    # status = data_api.status_code

    # if not (200 <= status < 300):
        # eprint(f"Error estado API: {status}")
        # print(f"\nCabecera:\n{data_api.headers}\nContenido:\n{data_api.text}\n")
        # sys.exit(1)
    # else:
        # pass
        # # print(f"Respuesta cruda: {data_api}")

# # .json() ya devuelve un dict, no es necesario json.loads()
print(data_api)
data = data_api.json()

# # Pretty print en stderr
eprint("=> Respuesta formateada:")
eprint(json.dumps(data, indent=4, ensure_ascii=False))

# # Obtener la lista de resultados
del data["Result"]
print(data)



# Recorrer con un for (aunque bastaría con resultados[0])
# for i, item in enumerate(resultados):
#     print(f'Identificacion: {item["Identification"]}')
