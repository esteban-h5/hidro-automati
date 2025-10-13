"""
Copiar archivos de configuracion con nuevas variables, dejando como persistente (Copiar y reemplazar) archivos de registro
"""

try:
    import os, shutil, time, zipfile, importlib.util
    from tkinter.filedialog import askopenfile
    from pathlib import Path
    
except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)  

#Devolver diccionario con variables del código
def GetConfig(dirConfig):
    with open(dirConfig,"r",encoding="latin-1") as configTXT:
        lineas = [_.split(":") for _ in configTXT.read().split("\n") if "#" not in _ and _ != ""]
        configDict = {}

        for items in lineas:
            
            llave = items[0].replace("\t","")
            valor = ":".join(items[1:]).replace("\t","")
            
            try:
                configDict[llave] = int(valor)
            except ValueError:
                configDict[llave] = valor

            if "true" in str(valor).lower() or "verdadero" in str(valor).lower():
                configDict[llave] = True
            
            if "false" in str(valor).lower() or "falso" in str(valor).lower():
                configDict[llave] = False 

    return configDict

try:
    zip_actual = "#####"
    ignore = []

    n_DM = "Descarga Muestras"
    n_RP = "Registros Pendientes"
    n_CL = "Cambiar Lotes"
    n_CE = "Copia Envases"
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
        os.path.join(n_il,"global_config.txt"),
    ]
    fOtros = [
        os.path.join(n_il,"Excepciones.xlsx"),
        os.path.join(n_il,"Param.env"),
    ]
    dirOtros_persistentes = [
        os.path.join(n_DM,"log"),
        os.path.join(n_DM,"Descargados"),
        os.path.join(n_CL,"log"),
        os.path.join(n_CL,"Descargados"),
        os.path.join(n_CE,"log"),
    ]
    
    dir_actual = os.path.realpath( os.path.join( os.path.dirname(os.path.realpath(__file__)),"..") )
    update_config = GetConfig(os.path.join(dir_actual,"Python Install","config_actualizar.txt"))

    excluir = [os.path.normpath(_) for _ in update_config["ExcluirArchivos"].split(",")]

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

    lista_config_old = [os.path.join(dir_actual,_) for _ in config]
    zip_dir = os.path.abspath(os.path.join(dir_actual, ".."))

    lista_archivos_persistentes_old = []
    lista_archivos_persistentes_new = []

    #Descomprimir archivos
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_actual = os.path.join(zip_dir, zip_ref.namelist()[0].split("/")[0])

        lista_config_new = [os.path.join(zip_actual,_) for _ in config]

        if not os.path.exists(zip_actual): 
            zip_ref.extractall(zip_dir)
        else:
            input(f"El nombre del directorio zip {zip_actual} ya existe")
            exit(1)

    for _ in config + xlsxDescarga + xlsxRegistros + fOtros:
        archivo = os.path.join(dir_actual,_)
        if not os.path.exists(archivo):
            print(f"El archivo persistente {archivo} no existe")
        if _ in excluir:
            print(f"Archivo persistente {_} para excluir")
        else:
            lista_archivos_persistentes_old.append(archivo)
            lista_archivos_persistentes_new.append(os.path.join(zip_actual,_))

    print(f"Programa descomprimido en {zip_dir}")
            
    #Obtener versión del programa nuevo
    version_file_path = None
    for root, dirs, files in os.walk(zip_actual):
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
        dict_old = GetConfig(lista_config_old[idx])
        dict_new = GetConfig(lista_config_new[idx])
        for key in dict_new.keys():
            if key not in dict_old.keys():
                print(f"Nuevo valor: {key}")
                cambio = cambio+f"\n{key}: {dict_new[key]}\n"
        dict_cambio[lista_config_new[idx]] = cambio

    #Eliminar archivos persistentes de zip nuevo y copiar archivos persistentes de programa viejo
    print(f"Reemplazando {len(lista_archivos_persistentes_new)} archivos en \n{zip_actual}")
    for idx in range(len(lista_archivos_persistentes_new)):
        archivo_old = lista_archivos_persistentes_old[idx]
        archivo_new = lista_archivos_persistentes_new[idx]

        if os.path.exists(archivo_old):
            if os.path.exists(archivo_new): os.remove(archivo_new)
            if os.path.exists(archivo_old): shutil.copy2(archivo_old, archivo_new)
            
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
        dir_new = os.path.join(zip_actual, dirOtros_persistentes[idx])

        if os.path.exists(dir_old):
            shutil.rmtree(dir_new, ignore_errors=True)
            shutil.copytree(dir_old, dir_new)
            print(f"{dir_old} => {dir_new}")
        else:
            print(f"Ya no existe: {dir_old}")
    
    os.startfile(zip_actual)
    input(f"{os.path.basename(zip_actual)} descomprimido correctamente, enter para salir...")

except Exception as e:
  print(e)
  input("Error, enter para salir...")