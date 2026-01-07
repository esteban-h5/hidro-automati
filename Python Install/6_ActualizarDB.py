
try:
    import os, sys, math
    import pandas as pd
    
except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)  

PI_wd               =   os.path.dirname(os.path.realpath(__file__))
internal_lib        =   os.path.normpath(os.path.join(PI_wd,"..","internal_lib"))

sys.path.insert(0, internal_lib)

from __myLIMS_API__ import get_methodprerequisite, get_methods
from __myLIMS_modulos__ import GetConfig, get

token = get('mylims_app', 'secret7')

global_config       =   GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )
paisActual      = global_config.get("paisActual", "").replace("é","e").replace("ú","u").lower()

log             = global_config.get("ActivarLOG", True)
APIdomain       = global_config.get("api-url", "")
rows = []

page_size = 50
page = 1

# primera llamada para saber el total
apiMetodos = get_methods(page, APIdomain=APIdomain, token=token)
total = apiMetodos.TotalCount

total_pages = math.ceil(total / page_size)

print(f"Total métodos: {total}")
print(f"Total páginas: {total_pages}")

for page in range(1, total_pages + 1):
    print(f"Consultando página {page}/{total_pages}")

    apiMetodos = get_methods(page, APIdomain=APIdomain, token=token)

    for metodo in apiMetodos.Result:
        rows.append({
            "MethodIdentification": metodo.Method.Identification,
            "MethodId": metodo.Method.Id,
            "InfoIdentification": metodo.Info.Identification,
            "InfoId": metodo.Info.Id,
        })

# crear DataFrame
df_salida = pd.DataFrame(rows)

# guardar a Excel
ruta_salida = os.path.join(internal_lib, "__MethodsDB__.xlsx")
df_salida.to_excel(ruta_salida, index=False)

print(f"Archivo generado: {ruta_salida}")