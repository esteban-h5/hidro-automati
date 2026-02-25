"""
Copiar archivos de configuracion con nuevas variables, dejando como persistente (Copiar y reemplazar) archivos de registro
"""

try:
    import os, shutil, time, zipfile, importlib.util, traceback, re, glob
    from tkinter.filedialog import askopenfile
    from pathlib import Path
    
except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)  

FLAG_ERRORES = False

#Devolver diccionario con variables del código
def GetConfig(dirConfig, encode="utf-8"):
  
    with open(dirConfig, "r", encoding=encode) as configTXT:
        lineas = []
        for linea in configTXT.read().split("\n"):

            if linea == "" or linea[0] == "#": continue
            if "#" in linea: linea = linea.split("#")[0].strip()
                
            lineas.append( linea.split(":") )
        
        configDict = {}

        for items in lineas:
            
            llave = items[0].strip()
            valor = ":".join(items[1:]).strip()
            
            if valor.isdigit():
                configDict[llave] = int(valor)
                continue

            elif str(valor).lower() in ("true", "verdadero"):
                configDict[llave] = True
                continue

            elif str(valor).lower() in ("false", "falso"):
                configDict[llave] = False
                continue
            
            else:
                configDict[llave] = valor

    return configDict
try:
    zip_actual = "#####"
    ignore = []
    save_pattern = re.compile(r"save_Param_(\d+)\.env$")

    n_DM = "Descarga Muestras"
    n_RP = "Registros Pendientes"
    n_CL = "Cambiar Lotes"
    n_CE = "Copia Envases"
    n_CM = "Crear Muestras"
    n_il = "internal_lib"

    xlsxDescarga = [
        os.path.join(n_DM,"Registro.xlsx"),
        os.path.join(n_DM,"Historico.xlsx"),
    ]
    xlsxRegistros = [
        os.path.join(n_RP,"RegistroSalida.xlsx"),
        os.path.join(n_RP,"RegistroAuxiliar.xlsx"),
        os.path.join(n_CL,"ListaMuestras.xlsx"),
        os.path.join(n_CE,"ListaEntrada.xlsx"),
    ]       
    config = [
        os.path.join(n_RP,"config.txt"),
        os.path.join(n_DM,"config.txt"),
        os.path.join(n_CL,"config.txt"),
        os.path.join(n_CE,"config.txt"),
        os.path.join(n_CM,"config.txt"),
        os.path.join(n_il,"global_config.txt"),
    ]
    dirOtros_persistentes = [
        os.path.join(n_DM,"log"),
        os.path.join(n_DM,"Descargados"),
        os.path.join(n_CL,"log"),
        os.path.join(n_CL,"Descargados"),
        os.path.join(n_CE,"log"),
        os.path.join(n_CM,"log"),
    ]
    fOtros = [
        os.path.join(n_il,"Excepciones.xlsx"),
        os.path.join(n_il,"Param.env"),
    ]

    #./Automatizacion actual/.
    dir_actual = os.path.realpath( os.path.join( os.path.dirname(os.path.realpath(__file__)),"..") )
    update_config = GetConfig(os.path.join(dir_actual,"Python Install","config_actualizar.txt"))

    for fname in os.listdir(os.path.join(dir_actual,n_il)):
        if save_pattern.match(fname):
            fOtros.append(os.path.join(n_il, fname))

    # excluir = [os.path.normpath(_) for _ in update_config["ExcluirArchivos"].split(",")]
    excluir = []
    
    for item in update_config["ExcluirArchivos"].split(","):
        item = os.path.normpath(item.strip())

        if "*" in item or "?" in item:
            archivos = glob.glob(os.path.join(dir_actual, item), recursive=True)
            excluir.extend([f"{os.path.basename(os.path.dirname(a))}\\{os.path.basename(a)}" for a in archivos])
        else:
            excluir.append(item)

        if "Automatizacion" not in os.path.basename(dir_actual):
            input("Archivo de actualizacion no se encuentra en la carpeta de automatización")
            exit(1)

    #Archivo de actualizacion
    print("Seleccionar archivo zip de programa nuevo")
    zip_file = askopenfile(title='Seleccionar Archivo ZIP actualización')

    if zip_file == None: exit(1)
    else: zip_file = zip_file.name

    if ".zip" not in zip_file:
        input("No se ha seleccionado un archivo .zip") 
        exit(1)
        
    lista_archivos_persistentes_old = []
    lista_archivos_persistentes_new = []
    
    zip_name = os.path.splitext(os.path.basename(zip_file))[0]
    
    #Directorio donde se dejara nuevo programa
    dir_zip = os.path.normpath(os.path.join(dir_actual,"..", zip_name))
    
    if not os.path.exists(dir_zip):
        os.mkdir(dir_zip)
    else:
        input("Directorio objetivo para descomprimir existe, enter para cerrar...")
        exit(1)
        
    #Descomprimir archivos
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(dir_zip)
    
    subdir = os.path.join(dir_zip,os.path.basename(dir_zip))
    if os.path.exists(subdir):
        dir_zip = subdir

    lista_config_new = [os.path.join(dir_zip,_) for _ in config]
    lista_config_old = [os.path.join(dir_actual,_) for _ in config]
    
    for _ in config + xlsxDescarga + xlsxRegistros + fOtros:
        archivo = os.path.join(dir_actual,_)

        if not os.path.exists(archivo):
            print(f"El archivo persistente {archivo} no existe")
            FLAG_ERRORES = True

        if _ in excluir:
            print(f"Archivo persistente {_} para excluir")
        
        else:
            lista_archivos_persistentes_old.append(archivo)
            lista_archivos_persistentes_new.append(os.path.join(dir_zip,_))

    print(f"Programa descomprimido en {dir_zip}")
    #Obtener versión del programa nuevo
    
    version_file_path = None
    for root, dirs, files in os.walk(dir_zip):
        for file in files:
            if file == "__version_info__.py":
                version_file_path = os.path.join(root, file)
                break
        if version_file_path:
            break
            
    if version_file_path:
        spec = importlib.util.spec_from_file_location("version_mod", version_file_path)
        version_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(version_mod)
        nueva_version = version_mod.version_actual
        print(f"Creando nueva versión: {nueva_version}")
        
    else:
        input("No se encontró __version_info__.py, Enter para cerrar...")
        exit(1)
    
    time.sleep(1)

    #Revisar variables de config y agregarlas a nuevo config en caso de no existir
    print("Revisando variables nuevas en archivos config")
    dict_cambio={}
    cambio = ""        

    for idx in range(len(lista_config_new)):
        config_old = lista_config_old[idx]
        config_old_name = os.path.basename(os.path.dirname(lista_config_old[idx]))+" VIEJO"
        
        config_new = lista_config_new[idx]
        config_new_name = os.path.basename(os.path.dirname(lista_config_new[idx]))+" NUEVO"
        try:
            dict_old = GetConfig(config_old)
            dict_new = GetConfig(config_new)
        except FileNotFoundError as e:
            print(f":{e}:")
            FLAG_ERRORES = True
            continue
        
        for key in dict_new.keys():
            if key not in dict_old.keys():
                print(f"Nuevo valor en {config_old_name}: {key}")
                cambio = cambio+f"\n{key}: {dict_new[key]}\n"

        for key in dict_old.keys():
            if key not in dict_new.keys():
                print(f"Valor descartado en {config_new_name}: {key}")

        dict_cambio[config_new] = cambio

    #Eliminar archivos persistentes de zip nuevo y copiar archivos persistentes de programa viejo
    print(f"Reemplazando {len(lista_archivos_persistentes_new)} archivos en \n{dir_zip}")
    
    for idx in range(len(lista_archivos_persistentes_new)):
        archivo_old = lista_archivos_persistentes_old[idx]
        archivo_new = lista_archivos_persistentes_new[idx]
        
        if os.path.exists(archivo_old):
            if os.path.exists(archivo_new): os.remove(archivo_new)
            if os.path.exists(archivo_old): 
                try:
                    shutil.copy2(archivo_old, archivo_new)
                except FileNotFoundError as e:
                    print(f":{e}:")
                    FLAG_ERRORES = True
                    continue

            #Agregar config
            if archivo_new in dict_cambio.keys():
                with open(archivo_new, 'a') as file:
                    file.write(dict_cambio[archivo_new])
                
            print(f"{archivo_old} => {archivo_new}")
        else:
            print(f"Ya no existe: {archivo_old}")


    #Copiar directorios persistentes
    for idx in range(len(dirOtros_persistentes)):
        dir_old = os.path.join(dir_actual, dirOtros_persistentes[idx])
        dir_new = os.path.join(dir_zip, dirOtros_persistentes[idx])
        
        if os.path.exists(dir_old):
            shutil.rmtree(dir_new, ignore_errors=True)
            shutil.copytree(dir_old, dir_new)
            print(f"{dir_old} => {dir_new}")
        else:
            print(f"Ya no existe: {dir_old}")
    
    os.startfile(dir_zip)
    if FLAG_ERRORES:
        input(f"{os.path.basename(dir_zip)} descomprimido con ERRORES, enter para salir...")
    else:
        input(f"{os.path.basename(dir_zip)} descomprimido correctamente, enter para salir...")

except Exception as e:
  print(e)
  traceback.print_exc()
  input("Error, enter para salir...")


""" ACTUALIZAR BASE DE DATOS

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

"""