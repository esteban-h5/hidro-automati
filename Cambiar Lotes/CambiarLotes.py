try:
    from selenium.webdriver.common.alert import Alert
    from selenium.common.exceptions import *
    from tkinter import messagebox
    from datetime import datetime
    import subprocess, os, sys
    from time import sleep

except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)

file_name           =   os.path.basename(__file__)

CL_wd               =   os.path.dirname(os.path.realpath(__file__))

internal_lib        =   os.path.normpath(os.path.join(CL_wd,"..","internal_lib"))
DM_wd               =   os.path.normpath(os.path.join(CL_wd,"..","Descarga Muestras"))
RP_wd               =   os.path.normpath(os.path.join(CL_wd,"..","Registros Pendientes"))

sys.path.insert(0, internal_lib)

from __myLIMS_modulos__ import *
from __myLIMS_wrappers__ import *
from __ficheros_modulos__ import *

########################################
#Inicialización de Config
########################################

config              =   GetConfig( dirConfig=os.path.join(CL_wd,"config.txt") )
global_config       =   GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )

keys_used = [
    "SoloBuscarControles", "RevisarRutinas", "RepasarEstado", "Registrar",
    "EstadoMuestras", "SaltarMuestra", "PublicarDescargables",
    "DescargarPublicadas", "filtro", "DOC_REVISION_ETFA_ID_CL",
    "DOC_REVISION_ID_CL", "nombreExcelListaMetodos",
    "nombreExcelListaRequerimientos", "nombreExcelEntrada",
    "nombreExcelHistorico", "nombreExcelEstados", "nombreExcelAuxiliar"
]

keys_used_g = [
    "myLIMSdomain", "Labsoftdomain", "paisActual", "ActivarLOG",
    "AppExcel", "InicioJornada", "ExtensionJornada",
    "ListaMensajesRutina", "ListaMensajesHoras"
]  

for key in keys_used:
    if key not in config.keys():
        input(f"Valor de config \'{key}\' no encontrado en archivo config, enter para continuar igualmente...")
for key in keys_used_g:
    if key not in global_config.keys():
        input(f"Valor de config \'{key}\' no encontrado en archivo global_config, enter para continuar igualmente...")

myLIMSdomain = global_config.get("myLIMSdomain", "")
Labsoftdomain = global_config.get("Labsoftdomain", "")

paisActual = global_config.get("paisActual", "").replace("é", "e").replace("ú", "u").lower()
log = global_config.get("ActivarLOG", False)
app_excel = global_config.get("AppExcel", "")

INICIO_JORNADA = global_config.get("InicioJornada", "")
EXTENSION_JORNADA = global_config.get("ExtensionJornada", "")

tipo_rutinas = global_config.get("ListaMensajesRutina", "").lower().split(",") if global_config.get("ListaMensajesRutina") else []
tipo_horas = global_config.get("ListaMensajesHoras", "").lower().split(",") if global_config.get("ListaMensajesHoras") else []

SoloBuscarControles = config.get("SoloBuscarControles", True)
RevisarRutinas = config.get("RevisarRutinas", True)
RepasarEstado = config.get("RepasarEstado", False)
Registrar = config.get("Registrar", True)

estadoMuestras = config.get("EstadoMuestras", "")
estadoMuestras = estadoMuestras.split(",") if estadoMuestras else []

SaltarMuestra = config.get("SaltarMuestra", True)

AutoPublicar = config.get("PublicarDescargables", False)
DescargarPublicadas = config.get("DescargarPublicadas", False)
filtroActual = config.get("filtro", "finalizadas").replace("é", "e").replace("ú", "u").lower()

timeout = 120

id_etfa_config = str(config.get("DOC_REVISION_ETFA_ID_CL", "")).split(",") if config.get("DOC_REVISION_ETFA_ID_CL") else []
id_no_etfa_config = str(config.get("DOC_REVISION_ID_CL", "")).split(",") if config.get("DOC_REVISION_ID_CL") else []

nombre_columnas = ["ID MUESTRAS", "ESTADO"]
nombre_columnas_reg = ["ID", "ID MUESTRAS", "TIENE CONTROLES", "TIENE RUTINAS", "MARCA"]
nombre_columnas_id = ["ID MUESTRAS"]

nombreLOG = os.path.join(CL_wd, "log", datetime.now().strftime('reporte_%Y_%m_%d-%H_%M'))

nombreExcelListaMetodos = config.get("nombreExcelListaMetodos", "")
dirExcelListaMetodos = os.path.join(CL_wd, nombreExcelListaMetodos) if nombreExcelListaMetodos else ""

nombreExcelListaRequerimientos = config.get("nombreExcelListaRequerimientos", "")
dirExcelListaRequerimientos = os.path.join(CL_wd, nombreExcelListaRequerimientos) if nombreExcelListaRequerimientos else ""

nombreExcelEntrada = config.get("nombreExcelEntrada", "")  # Rutinas
dirExcelEntrada = os.path.join(CL_wd, nombreExcelEntrada) if nombreExcelEntrada else ""

nombreExcelHistorico = config.get("nombreExcelHistorico", "")  # Historico
dirExcelHistorico = os.path.join(DM_wd, nombreExcelHistorico) if nombreExcelHistorico else ""

nombreExcelEstados = config.get("nombreExcelEstados", "")  # Estados
dirExcelEstados = os.path.join(DM_wd, nombreExcelEstados) if nombreExcelEstados else ""

nombreExcelAuxiliar = config.get("nombreExcelAuxiliar", "")  # Controles
dirExcelAuxiliar = os.path.join(RP_wd, nombreExcelAuxiliar) if nombreExcelAuxiliar else ""

if log:
    print("Historial de log activo\n")
    
    if not os.path.isdir( os.path.join(CL_wd,"log") ): os.mkdir(os.path.join(CL_wd,"log"))

    def eprint(string="", end="\n"):
        utf = str(string).replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        print(f"\n{datetime.now().strftime(f'[%H:%M:%S] [{version_actual}]')}\n"+utf, end=end, file=sys.stderr)
        print(string, end=end)
    
    def logprint(string="", end="\n"):
        utf = str(string).replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
        print(f"\n{datetime.now().strftime(f'[%H:%M:%S] [{version_actual}] [log]')}\n"+utf, end=end, file=sys.stderr)

    log_file = open(nombreLOG+".txt", "a")
    sys.stderr = log_file

    def slog():
        print(f"\n{datetime.now().strftime(f'[%H:%M:%S] [LOG RECARGADO] [log]')}", file=sys.stderr)
        global log_file
        log_file.flush()
        log_file.close()
        log_file = open(nombreLOG+".txt", "a")
        sys.stderr = log_file

else:
    print("Historial de log desactivado\n")
    eprint = print
    logprint = print
    slog = lambda _ : None

if os.path.exists(os.path.join(internal_lib, "hidro-env") ) and sys.prefix == sys.base_prefix:
    eprint("SE HA CREADO VENV PERO NO SE ESTA USANDO\n")

MensajeInicial(file_name, funcion_print=eprint, config=config, global_config=global_config, funcion_log=logprint )

eprint(f"País Actual: {paisActual}\n")

if not existe_param_env(internal_lib):
    eprint("Error No se encontró archivo con credenciales. (Param.env)")
    input("Enter para cerrar..")
    exit(1)

# tkMenu      =   lambda x,y="-",z="-": int(subprocess.run(["python", f"{internal_lib}\\__display_modulos__.py","2",str(x),str(y),str(z)], capture_output=True, text=True).stdout)
tkMenu      =   lambda x1, x2="-", x3="-", x4="-", x5="-": subprocess.run(["python", f"{internal_lib}\\__display_modulos__.py","2",str(x1),str(x2),str(x3),str(x4),str(x5)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
ptkMenu      =   lambda x1, x2="-", x3="-", x4="-", x5="-": eprint(f"python \"{internal_lib}\\__display_modulos__.py\" 2 \"{str(x1)}\" \"{str(x2)}\" \"{str(x3)}\" \"{str(x4)}\" \"{str(x5)}\"")

xpath_muestra_activa    = "//div[@id='InterfaceContent']/div[1]//div[@class='labsoft-ui-input checkbox']//input[@data-test='Active']"
xpath_estado_muestra    = "//div[@id='InterfaceContent']/div[1]//label[contains(text(),'Estatus de la Muestra')]/following-sibling::span[contains(@class, 'k-combobox')]/span/input[@role='combobox']"
xpath_lista_analitos    = "//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody"
x_path_alerta_inactiva  = "//*/div[contains(@class,'k-window') and contains(@style,'display: block;')]//span[@class='k-window-title' and contains(text(), 'Registro Inactivo')]/ancestor::div[contains(@class,'k-window') and contains(@style,'display: block;')]"

df_entrada          =   AbrirXLSX(dirExcelEntrada, colnames=nombre_columnas)
dir_Descargados     =   os.path.join(CL_wd, "Descargados")

if not RepasarEstado: #Obtener solo muestras que no tengan estado [LISTO, ERROR]
    muestras_entrada = df_entrada[df_entrada["ESTADO"].astype(str).str.strip() == ""]["ID MUESTRAS"].to_list()
else: 
    muestras_entrada = df_entrada["ID MUESTRAS"].to_list()

muestras_requerimientos = pd.read_excel(dirExcelListaRequerimientos)
cantidad_muestras = len(muestras_entrada)

def excepcion_handler(e, id_muestra=None, driver=None, funcion_print=print):
    tipoError = type(e).__name__
    str_expt = f"Error {tipoError} en ejecucion" if id_muestra == None else f"Error {tipoError} para la muestra {id_muestra}"

    if driver != None:
        ventana_dim = driver.get_window_size()
        str_expt = str_expt+f"...\nTamaño ventana: {ventana_dim['width']}x{ventana_dim['height']}\n\n"
        str_expt = str_expt+":\n\n "
    
    str_expt = str_expt+FormatoExcepcion(e)

    if Registrar and id_muestra != None: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR")
    notify(title=f"Problemas con la muestra {id_muestra}!", body=tipoError)
    eprint(str_expt)
    sleep(3)

def secuencia_inicio():
    global prefs
    prefs = prefs | {}
    DriverOptions.add_experimental_option("prefs",prefs)

    while ComprobarExcelAbierto(dirExcelEntrada,colnames=nombre_columnas):
        eprint("Error de permisos, excel abierto")
        messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")

    for _ in range(5):
        try:
            driver = Chrome(options=DriverOptions)
            break
        except SessionNotCreatedException as e:
            eprint("No se pudo iniciar el navegador, reintentando...")
            sleep(1)
    else:
        eprint("Navegador no se pudo iniciar, error inesperado: {e}")
        exit(1)

    eprint("Iniciando sesión en labsoft")
    try:
        Login(driver, path_internal=internal_lib, post_url=myLIMSdomain, login_url=Labsoftdomain)
        EsperarCARGA_myLIMS(driver, reintentos=5)

    except ExcepcionDeCarga as e:
        eprint(f"Error al cargar la página\n\n{e}")
        notify(title="Error al cargar la página", body=type(e).__name__)
        Logout(driver,logout_url=Labsoftdomain)
        exit(1)

    print("Ctrl+C para Interrumpir el programa")
    return driver


def secuencia_estado_muestra(driver, id_muestra, idx=None, total=None, estados=estadoMuestras):              
    
    if idx != None and total != None:
        eprint(f"\n[{idx+1}/{total}] Revisando muestra {id_muestra}")
    else: 
        eprint(f"\nRevisando muestra {id_muestra}")

    driver.get(f"{myLIMSdomain}Main.cshtml#Sample/Details/{id_muestra}")
    EsperarCARGA_myLIMS(driver)
        
    muestra_activa = driver.find_element(By.XPATH, xpath_muestra_activa ).is_selected()

    if not muestra_activa:
        eprint(f"Muestra desactivada, saltando...")
        driver.get(myLIMSdomain)

        try:
            alerta = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, x_path_alerta_inactiva)))
            boton = alerta.find_element(By.XPATH,".//div[@class='btn-group labsoft-ui-buttons-group']//button[data-test='Continuar']").click()
            boton.click()

        except TimeoutException:
            pass

        return -1

    muestra_estado = driver.find_element(By.XPATH, xpath_estado_muestra ).get_attribute("value")
    logprint(f"Estado de la muestra {id_muestra}: {muestra_estado}")

    if muestra_estado not in estados:
        eprint(f"Muestra en estado {muestra_estado}, se eperaba {estados}, saltando...\n")
        return -1
    
while True:
    slog()
    eprint("Menú Principal")
    menu_principal = tkMenu(0, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual)
    logprint(f"Salida del menu: {menu_principal}\n")

    try:
        #PARA SUBMENU 7
        if "|" in menu_principal:
            n_menu_principal = int(menu_principal.split("|")[0]) 
            opcion_Fecha = menu_principal.split("|")[1]

        else:
            n_menu_principal = int(menu_principal)

    except ValueError as e:
        messagebox.showerror(title="Error", message=f"Error inesperado al obtener información del menu: {menu_principal}\n\n{e}")

    match n_menu_principal:

        ################################################################################################################################################################################################
        # MODIFICAR MUESTRAS
        ################################################################################################################################################################################################

        ####################
        #Reemplazar método de análisis para un parámetro con el mismo nombre
        case 1:
            eprint(f"{n_menu_principal}: Reemplazar uno o más métodos por otro método de análisis para {cantidad_muestras} muestras")

            #Obtener opcion a partir de menu
            # str_cambio = ptkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual)
            str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            while str_cambio == "-2":
                str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            if str_cambio == "-1" or str_cambio == "":
                #Volviendo
                pass

            else:
                if "&" not in str_cambio:
                    raise ExcepcionDeCarga(f"No se recibio formato correcto de menu: [{str_cambio}]")
                
                if "|" in str_cambio:
                    metodos_principales = str_cambio.split("|")[0]
                    metodo_antiguo, metodo_nuevo, cambiar_u_medida, analisis = metodos_principales.split("&")

                    #Asignar a diccionario con cada llave-valor analisis-metodo de requerimiento
                    metodos_extra = {_.split("&")[0]:_.split("&")[1] for _ in str_cambio.split("|")[1:]}

                else:
                    metodo_antiguo, metodo_nuevo, cambiar_u_medida, analisis = str_cambio.split("&")
                    metodos_extra = {}
                
                cambiar_u_medida = (cambiar_u_medida == "True")

                if ";" in metodo_antiguo:
                    metodos_antiguos = metodo_antiguo.split(";")
                else:
                    metodos_antiguos = [metodo_antiguo]

                if metodo_nuevo in metodos_antiguos:
                    eprint("Los metodos no pueden ser iguales")
                    
                else:
                    # requerimientos_nuevos = muestras_requerimientos[muestras_requerimientos["Metodo"] == metodo_nuevo]["AnalisRequerido"].to_list()
                    str_anuncio = f"Cambiando de \"{metodos_antiguos}\" a \"{metodo_nuevo}\" para {cantidad_muestras} muestras"
                    
                    if cambiar_u_medida:
                        str_anuncio = str_anuncio+" revisando unidad de medida"
                    
                    if analisis:
                        str_anuncio = f"{str_anuncio} y restringiendo analito {analisis}"

                    eprint(str_anuncio+"\n")

                    #Inicio Navegador 
                    try:
                        from __myLIMS_modulos__  import *
                        driver = secuencia_inicio()

                        for idx,id_muestra in enumerate(muestras_entrada):

                            try:
                                flag_estado = secuencia_estado_muestra(driver, id_muestra,  idx=idx,  total=cantidad_muestras)
                                if flag_estado == -1: 
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SALTADA")
                                    continue

                                BotonSection(driver,"SectionAnalysis", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)

                                if analisis != "":
                                    filas_entrada = get_analito_dict(driver, metodos=metodos_antiguos, analitos=[analisis])
                                else:
                                    filas_entrada = get_analito_dict(driver, metodos=metodos_antiguos, analitos=[])

                                if len(filas_entrada) == 0:
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO")
                                    eprint(f"No se encontró el método {metodos_antiguos} en la muestra. Saltando edición...\n")
                                    continue
                                
                                eprint(f"Analitos encontrados: {len(filas_entrada)}")
                                
                                BotonSection(driver,"SectionAnalysis", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)

                                #Modo edición
                                driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                                EsperarCARGA_myLIMS(driver)

                                ################################################
                                #Alterar metodo y cambiar por metodo de entrada
                                flag_estado = edit_alterar_por_metodo(driver, analito_dict=filas_entrada, nuevo_metodo=metodo_nuevo)
                                
                                if flag_estado == -1: 
                                    # eprint(f"Metodo {metodo_nuevo} no encontrado para analito numero {analito['id']} con metodo {analito['metodo']}")
                                    eprint(f"Metodo {metodo_nuevo} no encontrado")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO")
                                    
                                    BotonAccion(driver,"CancelButton", log=True, funcion_print=logprint ).click()
                                    EsperarCARGA_myLIMS(driver)                             
                                    continue

                                if flag_estado == -2: 
                                    # eprint(f"Metodo {metodo_nuevo} no encontrado para analito numero {analito['id']} con metodo {analito['metodo']}")
                                    eprint(f"Metodo {metodo_nuevo} no se puede alterar")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "METODO NO ALT")
                                    
                                    BotonAccion(driver,"CancelButton", log=True, funcion_print=logprint ).click()
                                    EsperarCARGA_myLIMS(driver)                             
                                    continue

                                BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)

                                str_salida = "\n".join([f" -> {_['analisis']} - {_['metodo']} - {_['medida']}" for _ in filas_entrada])

                                # eprint(f"\nAnalito de método {analito['metodo']} y análisis {analito['analisis']} editado para muestra {id_muestra}")
                                eprint(f"\neditado en la muestra {id_muestra}:\n{str_salida}")

                                ##########################
                                #Revisar unidad de medida:
                                if "Subcontrato" in "".join(metodos_antiguos) and cambiar_u_medida:
                                    eprint(f"Metodo Subcontrato, saltando revision de medida\n")

                                else:
                                    if cambiar_u_medida:
                                        #Modo edición
                                        driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                                        EsperarCARGA_myLIMS(driver)

                                        for analito in filas_entrada:
                                            flag_estado = edit_revisar_medida(driver, analito_dict=analito, funcion_print=eprint)

                                            if flag_estado == -1: 
                                                eprint(f"Unidad de medida {analito['medida']} no encontrada para Metodo {metodo} en el analito numero {analito['id']} con metodo {analito['metodo']}")
                                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN U/MEDIDA")
                                                
                                                BotonAccion(driver,"CancelButton", log=True, funcion_print=logprint ).click()
                                                EsperarCARGA_myLIMS(driver)                             
                                                continue
                                                
                                            if flag_estado == 1: 
                                                eprint(f"Misma unidad de medida encontrada")
                                            
                                            if flag_estado == 0:
                                                eprint(f"Unidad de medida {analito['medida']} cambiada")
                                            
                                        BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint ).click()
                                        EsperarCARGA_myLIMS(driver)

                                # BotonSection(driver, "SectionLogistic", log=True, funcion_print=logprint ).click()
                                # EsperarCARGA_myLIMS(driver)
                                
                                # edit_aprobar_logistica(driver, nuevos_metodos=metodos_antiguos, funcion_print=eprint)
                            
                                eprint(f"\nMuestra {id_muestra} lista\n")
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "EDITADO")

                            except BaseException as e:
                                excepcion_handler(e, id_muestra, driver)

                        notify(title="Programa finalizado")
                        eprint(f"\nPrograma finalizado... Cerrando\n")
                        Logout(driver,logout_url=Labsoftdomain)
                        driver.quit()

                    except NoSuchWindowException:
                        eprint("Ventana de navegador cerrada")

                    except KeyboardInterrupt:
                        print("Programa interrumpido...\n Cerrando navegador")
                        Logout(driver,logout_url=Labsoftdomain)
                        driver.quit()

        ####################
        #Reemplazar analíto por otro con el mismo método de análisis
        case 2:
            eprint(f"{n_menu_principal}: Reemplazar analíto por otro con el mismo método de análisis para {cantidad_muestras} muestras")

            #Obtener opcion a partir de menu
            str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            while str_cambio == "-2":
                str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            if str_cambio == "-1" or str_cambio == "":
                #Volviendo
                pass
            
            else:
                #No esperar requerimientos, se agregará metodo antes de borrar
                analito_antiguo, analito_nuevo, metodo, cambiar_u_medida = str_cambio.split("&")
                cambiar_u_medida = (cambiar_u_medida == "True")

                if cambiar_u_medida:
                    eprint(f"Cambiando de \"{analito_antiguo}\" a \"{analito_nuevo}\" con el metodo {metodo} para {cantidad_muestras} muestras revisando unidad de medida\n")
                else:
                    eprint(f"Cambiando de \"{analito_antiguo}\" a \"{analito_nuevo}\" con el metodo {metodo} para {cantidad_muestras} muestras\n")
                
                #Inicio Navegador
                try:
                    from __myLIMS_modulos__  import *
                    driver = secuencia_inicio()

                    for idx,id_muestra in enumerate(muestras_entrada):

                        try:
                            flag_estado = secuencia_estado_muestra(driver, id_muestra,  idx=idx,  total=cantidad_muestras)
                            if flag_estado == -1: 
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SALTADA")
                                continue

                            BotonSection(driver,"SectionAnalysis", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                            filas_entrada = get_analito_dict(driver, metodos=[metodo], analitos=[analito_antiguo])

                            if len(filas_entrada) == 0:
                                eprint(f"No se encontró el método {metodo} con el analito {analito_antiguo} en la muestra. Saltando edición...")
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO-ANALITO")
                                continue

                            #Modo edición
                            driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                            EsperarCARGA_myLIMS(driver)
                            
                            for analito in filas_entrada:

                                ################################################
                                # Agregar nuevo analisis con mismo metodo y borrar analisis con metodo antiguo
                                flag_estado = edit_agregar_por_analisis_y_metodo(driver, analito_nuevo, metodo)

                                if flag_estado == -1: 
                                    eprint(f"Par Analito {analito_nuevo} y metodo {metodo} no encontrados en la muestra")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO-ANALITO")
                                    continue

                                ################################################
                                # Eliminar analisis antiguo con mismo metodo
                                flag_estado = edit_eliminar_por_analisis_dict(driver, analito)

                                if flag_estado == -1: 
                                    eprint(f"No se ha podido eliminar el analito numero {analito['id']} {analito['analito']} con metodo {analito['metodo']} ")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR DEL METODO")
                                    continue

                                if flag_estado == -2: 
                                    eprint(f"No se ha encontrado el metodo {analito['id']} {analito['analito']} para eliminarlo")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR DEL ANALISIS")
                                    continue
                                
                                ################################################
                                # Alterar metodo en caso de no ser el esperado

                                BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)

                                eprint(f"Muestra {id_muestra} editada\n")

                                ##########################
                                #Revisar unidad de medida:

                                if "Subcontrato" in metodo and cambiar_u_medida:
                                    eprint(f"Metodo Subcontrato, saltando revision de medida")

                                elif cambiar_u_medida:

                                    #Modo edición
                                    driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                                    EsperarCARGA_myLIMS(driver)

                                    flag_estado = edit_revisar_medida(driver, analito_dict=analito, funcion_print=eprint)
                                        
                                    if flag_estado == -1: 
                                        eprint(f"Unidad de medida {analito['medida']} no encontrada para Metodo {metodo} en el analito numero {analito['id']} con metodo {analito['metodo']}")
                                        if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN U/MEDIDA")
                                        BotonAccion(driver,"CancelButton", log=True, funcion_print=logprint ).click()
                                        continue
                                        
                                    if flag_estado == 1: 
                                        eprint(f"Misma unidad de medida encontrada")
                                    
                                    if flag_estado == 0:
                                        eprint(f"Unidad de medida {analito['medida']} cambiada")

                                    BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint ).click()
                                    EsperarCARGA_myLIMS(driver)
                                    

                                BotonSection(driver, "SectionLogistic", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)
                                
                                edit_aprobar_logistica(driver, nuevos_metodos=[metodo], funcion_print=eprint)

                        except BaseException as e:
                            excepcion_handler(e, id_muestra, driver)

                    notify(title="Programa finalizado")
                    eprint(f"Programa finalizado... Cerrando\n")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()

                except NoSuchWindowException:
                    eprint("Ventana de navegador cerrada")

                except KeyboardInterrupt:
                    print("Programa interrumpido...\n Cerrando navegador")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()
            pass

        ####################
        #Reemplazar un análisis por otro con otro método de análisis
        case 3:
            eprint(f"{n_menu_principal}: Reemplazar un análisis por otro con otro método de análisis para {cantidad_muestras} muestras")

            #Obtener opcion a partir de menu
            str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            while str_cambio == "-2":
                str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            if str_cambio == "-1" or str_cambio == "":
                #Volviendo
                pass

            else:
                #No esperar requerimientos, se agregará metodo antes de borrar
                analito_antiguo, analito_nuevo, metodo_antiguo, metodo_nuevo, cambiar_u_medida = str_cambio.split("&")
                cambiar_u_medida = (cambiar_u_medida == "True")

                eprint(f"Cambiando de \"{analito_antiguo}\" con {metodo_antiguo} a \"{analito_nuevo}\" con {metodo_nuevo} para {cantidad_muestras} muestras ",end="")
                
                if cambiar_u_medida:
                     eprint("revisando unidad de medida\n")
                else:
                    eprint("sin unidad de medida\n")

                #Inicio Navegador
                try:
                    from __myLIMS_modulos__  import *
                    driver = secuencia_inicio()

                    for idx,id_muestra in enumerate(muestras_entrada):

                        try:
                            flag_estado = secuencia_estado_muestra(driver, id_muestra,  idx=idx,  total=cantidad_muestras)
                            if flag_estado == -1: 
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SALTADA")
                                continue

                            BotonSection(driver,"SectionAnalysis", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                            filas_entrada = get_analito_dict(driver, metodos=[metodo_antiguo], analitos=[analito_antiguo])

                            if len(filas_entrada) == 0:
                                eprint(f"No se encontró el método {metodo_antiguo} con el analito {analito_antiguo} en la muestra. Saltando edición...")
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO-ANALITO")
                                continue

                            #Modo edición
                            driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                            EsperarCARGA_myLIMS(driver)
                            
                            for analito in filas_entrada:

                                ################################################
                                # Agregar nuevo analisis con mismo metodo y borrar analisis con metodo antiguo
                                flag_estado = edit_agregar_por_analisis_y_metodo(driver, analito_nuevo, metodo_nuevo)

                                if flag_estado == -1: 
                                    eprint(f"El {metodo_nuevo} con el analito {analito_nuevo} no disponibles para la muestra. Saltando edición...")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO-ANALITO")
                                    continue

                                ################################################
                                # Eliminar analisis antiguo con mismo metodo
                                flag_estado = edit_eliminar_por_analisis_dict(driver, analito)

                                if flag_estado == -1: 
                                    eprint(f"No se ha podido eliminar el analisis {analito['id']} {analito['analito']} con metodo {analito['metodo']} ")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR ")
                                    continue

                                if flag_estado == -2: 
                                    eprint(f"No se ha encontrado el analisis {analito['id']} {analito['analito']} con metodo {analito['metodo']} para eliminarlo")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR DEL ANALISIS")
                                    continue
                                
                                ################################################
                                # Alterar metodo en caso de no ser el esperado

                                BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)

                                eprint(f"Muestra {id_muestra} editada\n")

                                ##########################
                                #Revisar unidad de medida:

                                if "Subcontrato" in metodo_nuevo and cambiar_u_medida:
                                    eprint(f"Metodo Subcontrato, saltando revision de medida")

                                elif cambiar_u_medida:

                                    #Modo edición
                                    driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                                    EsperarCARGA_myLIMS(driver)

                                    flag_estado = edit_revisar_medida(driver, analito_dict=analito, funcion_print=eprint)
                                    
                                    if flag_estado == -1: 
                                        eprint(f"Unidad de medida {analito['medida']} no encontrada para Metodo {metodo} en el analito numero {analito['id']} con metodo {analito['metodo']}")
                                        if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN U/MEDIDA")
                                        BotonAccion(driver,"CancelButton", log=True, funcion_print=logprint ).click()
                                        continue
                                        
                                    if flag_estado == 1: 
                                        eprint(f"Misma unidad de medida encontrada")
                                    
                                    if flag_estado == 0:
                                        eprint(f"Unidad de medida {analito['medida']} cambiada")
                                    
                                    BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint ).click()
                                    EsperarCARGA_myLIMS(driver)

                                BotonSection(driver, "SectionLogistic", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)
                                
                                edit_aprobar_logistica(driver, nuevos_metodos=[metodo_nuevo], funcion_print=eprint)

                        except BaseException as e:
                            excepcion_handler(e, id_muestra, driver)

                    eprint(f"Programa finalizado... Cerrando\n")
                    notify(title="Programa finalizado")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()

                except NoSuchWindowException:
                    eprint("Ventana de navegador cerrada")

                except KeyboardInterrupt:
                    print("Programa interrumpido...\n Cerrando navegador")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()

        ####################
        # Agregar análisis a muestras en lista
        case 4:
            eprint(f"{n_menu_principal}: Agregar análisis a muestras en lista para {cantidad_muestras} muestras")
            
            str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))
            
            while str_cambio == "-2":
                str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            if str_cambio == "-1" or str_cambio == "":
                #Volviendo
                pass

            else:
                
                if "|" in str_cambio:
                    metodos_principales = str_cambio.split("|")
                    metodo_principal, analisis_principal = metodos_principales[0].split("&")

                    #Asignar a diccionario con cada llave-valor metodo-analisis de requerimiento
                    metodos_extra = {_.split("&")[0]:_.split("&")[1] for _ in metodos_principales[1:]}

                else:
                    #PRINT
                    metodo_principal, analisis_principal = str_cambio.split("&")
                    metodos_extra = {}
                
                eprint(f"Agregando metodo \"{metodo_principal}\" y analisis \"{analisis_principal}\" para {cantidad_muestras}\n")
                
                if metodos_extra != {}:
                    eprint(f"Aplicando también para los siguientes metodos:\n")
                    eprint("\n".join([f" - {llave}: {valor}" for llave, valor in metodos_extra.items()]), end="\n\n")

                #Inicio Navegador
                try:

                    from __myLIMS_modulos__  import *
                    driver = secuencia_inicio()

                    for idx, id_muestra in enumerate(muestras_entrada):
                        try:
                            metodos_req = list(metodos_extra.values())
                            analisis_req = list(metodos_extra.keys())
                            
                            flag_estado = secuencia_estado_muestra(driver, id_muestra, idx=idx,  total=cantidad_muestras, estados=estadoMuestras)
                            if flag_estado == -1: 
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SALTADA")
                                continue

                            BotonSection(driver,"SectionAnalysis", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                            #Obtener lista de analisis en navegador
                            conjunto_analisis_web = [analito.find_element(By.XPATH,"./td[@data-test='AnalysisGrid.Info.Identification']").text for analito in driver.find_elements(By.XPATH, "//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr")]
                            
                            if analisis_principal in conjunto_analisis_web:
                                eprint(f"El análisis {analisis_principal} ya existe en la muestra, saltando...")
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ANALISIS YA EXISTE")
                                continue

                            #Modo edición
                            driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                            EsperarCARGA_myLIMS(driver)

                            ################################################
                            #Agregar metodo y analisis principales
                            flag_estado = edit_agregar_por_analisis_y_metodo(driver, nuevo_analito=analisis_principal, metodo=metodo_principal)
                            
                            if flag_estado == -1: 
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN ANALITO PRINCIPAL")
                                continue
                            
                            ################################################
                            #Buscar nuevos requerimientos y asignar respectivo metodo
                            filas_entrada = get_analito_dict(driver, analitos=analisis_req)

                            for d_analito in filas_entrada:

                                flag_estado = edit_alterar_por_metodo(driver, analito_dict=d_analito, nuevo_metodo=metodos_extra[d_analito['analisis']])
                                
                                if flag_estado == -1: 
                                    eprint(f"Metodo {metodo_nuevo} no encontrado para analito numero {d_analito['id']} con metodo {analito['metodo']}")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO")
                                    continue

                            BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint).click()
                            EsperarCARGA_myLIMS(driver)

                            eprint(f"Muestra {id_muestra} editada\n")
                        
                        except BaseException as e:
                            excepcion_handler(e, id_muestra, driver)

                    eprint(f"Programa finalizado... Cerrando\n")
                    notify(title="Programa finalizado")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()

                except NoSuchWindowException:
                    eprint("Ventana de navegador cerrada")

                except KeyboardInterrupt:
                    eprint("Programa interrumpido...\n Cerrando navegador")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()
        
        ####################
        # Eliminar análisis de muestras en lista
        case 5:
            eprint(f"{n_menu_principal}: Eliminar método de muestras en lista para {cantidad_muestras} muestras")
            
            str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            while str_cambio == "-2":
                str_cambio = str(tkMenu(n_menu_principal, dirExcelListaMetodos, dirExcelListaRequerimientos, cantidad_muestras, paisActual))

            if str_cambio == "-1" or str_cambio == "":
                #Volviendo
                pass

            else:
                metodo = str_cambio

                #Inicio Navegador
                try:

                    from __myLIMS_modulos__  import *
                    driver = secuencia_inicio()

                    for idx,id_muestra in enumerate(muestras_entrada):

                        try:
                            flag_estado = secuencia_estado_muestra(driver, id_muestra,  idx=idx,  total=cantidad_muestras)
                            if flag_estado == -1: 
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SALTADA")
                                continue

                            BotonSection(driver,"SectionAnalysis", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                            filas_entrada = get_analito_dict(driver, metodos=[metodo])

                            #Modo edición
                            driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                            EsperarCARGA_myLIMS(driver)
                            
                            for analito in filas_entrada:
                                flag_estado = edit_eliminar_por_metodo_dict(driver, analito)
                                
                                if flag_estado == -1: 
                                    eprint(f"Metodo {metodo} no encontrado para analito numero {analito['id']} con metodo {analito['metodo']}")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SIN METODO")
                                    continue

                                if flag_estado == -2: 
                                    eprint(f"No se pudo hacer click en {metodo} con analito numero {analito['id']} con metodo {analito['metodo']}")
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR METODO CLICK")
                                    continue

                            BotonAccion(driver,"SaveButton", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                            eprint(f"Muestra {id_muestra} editada\n")

                        except BaseException as e:
                            excepcion_handler(e, id_muestra, driver)

                    eprint(f"\nPrograma finalizado... Cerrando\n")
                    notify(title="Programa finalizado")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()

                except NoSuchWindowException:
                    eprint("Ventana de navegador cerrada")

                except KeyboardInterrupt:
                    eprint("Programa interrumpido...\n Cerrando navegador")
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()

        ####################
        # Cambiar fecha Recibimiento
        case 6:
            eprint(f"{n_menu_principal}: Cambiar Fecha Recibimiento [{opcion_Fecha}] para {cantidad_muestras} muestras")
            try:
                from __myLIMS_modulos__  import *
                driver = secuencia_inicio()
                
                for idx,id_muestra in enumerate(muestras_entrada):
                    try:

                        flag_estado = secuencia_estado_muestra(driver, id_muestra, idx=idx,  total=cantidad_muestras, estados=estadoMuestras)
                        # flag_estado = secuencia_estado_muestra(driver, id_muestra)

                        if flag_estado == -1: 
                            if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SALTADA")
                            continue

                        fecha_muestreo = driver.find_element(By.XPATH, "//input[@data-test='TakenDateTime']").get_attribute("value")
                        
                        try:
                            BotonSection(driver,"Historial", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                        except ElementNotInteractableException:
                            driver.set_window_size(1300,800) 
                            BotonSection(driver,"Historial", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                        fecha_recepcion = ""
                        
                        for fila in driver.find_elements(By.XPATH, '//div[@id="InterfaceContent"]/div[not(contains(@style, "display:"))]/div[@class="row labsoft-ui-layoutrow"]/div[1]//tbody[@role="rowgroup"]/tr'):
                            n_fila = fila.find_element(By.XPATH, './td[@data-test="StatusHistoryGrid.SampleStatus.Identification"]').text
                            if "Recibida" == n_fila:
                                fecha_recepcion = ":".join(fila.find_element(By.XPATH, './td[@data-test="StatusHistoryGrid.EditionDateTime"]').text.replace("-", "/").split(":")[:-1])
                        
                        BotonAccion(driver,"EditSampleReceivedTimeButton", log=True, funcion_print=logprint ).click()
                        EsperarCARGA_myLIMS(driver,revisar_overlay=False)
                        
                        x_path_ventana = "//*/div[contains(@class,'k-window') and contains(@style,'display: block;')]"
                        x_path_ventana_alerta = x_path_ventana+"//span[@class='k-window-title' and contains(text(), 'Aviso')]/ancestor::div[contains(@class,'k-window') and contains(@style,'display: block;')]"
                        
                        ventana = driver.find_element(By.XPATH, x_path_ventana)
                        ventana_entrada = ventana.find_element(By.XPATH, f'.//input[@data-role="datetimepicker"]')

                        fecha_antigua = ventana_entrada.get_attribute("value")
                        
                        if ".m." in fecha_antigua and ".m." not in opcion_Fecha:
                            opcion_Fecha = datetime.strptime(opcion_Fecha, "%d-%m-%Y %H:%M:%S").strftime("%d/%m/%Y %I:%M:%S %p")
                            opcion_Fecha = opcion_Fecha.replace("AM", "a.m.").replace("PM", "p.m.")
                        
                        ventana_entrada.send_keys(Keys.CONTROL, "a")
                        ventana_entrada.send_keys(Keys.DELETE)
                        ventana_entrada.send_keys(opcion_Fecha)

                        BotonVentana(driver,"ChangeReceivedTimeButton", log=True, funcion_print=logprint ).click()
                        EsperarCARGA_myLIMS(driver,revisar_overlay=False)
                        sleep(.5)

                        #Esperar la precencia de y alertas
                        if SiExisteElemento(driver, atributo="", valor="", XPATH=x_path_ventana_alerta):

                            alerta = driver.find_element(By.XPATH, x_path_ventana_alerta)
                            mensaje = alerta.find_element(By.XPATH,".//div[@class='row labsoft-ui-layoutrow']/div[2]/div").text

                            logprint(f"mensaje: {mensaje}")

                            if "posterior" in mensaje: 
                                eprint(f"Nueva fecha {opcion_Fecha} anterior a fecha de muestreo [{fecha_muestreo}]")
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "POSTERIOR")
                                BotonVentana(driver,"Ok", log=True, funcion_print=logprint ).click()
                                BotonVentana(driver,"CancelReceivedTimeButton", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver,revisar_overlay=False)
                                continue

                            elif "inferior" in mensaje: 
                                eprint(f"Nueva fecha {opcion_Fecha} anterior a fecha previa de recibimiento [{fecha_recepcion}]")
                                driver.find_element(By.XPATH, x_path_ventana+'//textarea[@class="k-textbox"]').send_keys("Cambio Hora")
                                BotonVentana(driver,"Si", log=True, funcion_print=logprint ).click()
                                # BotonVentana(driver,"ChangeReceivedTimeButton").click()
                                EsperarCARGA_myLIMS(driver,revisar_overlay=False)

                            else:
                                raise ExcepcionDeMuestra(f"Muestras desconocida para {id_muestra}")
                            

                        if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "FECHA")
                        eprint(f"Recibimiento cambiado a {opcion_Fecha}\n")

                    except BaseException as e:
                        excepcion_handler(e, id_muestra, driver)
                        
                        driver.refresh()
                        EsperarCARGA_myLIMS(driver)
                        sleep(3)

                eprint(f"Programa finalizado... Cerrando\n")
                notify(title="Programa finalizado")
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()

            except NoSuchWindowException:
                eprint("Ventana de navegador cerrada")

            except KeyboardInterrupt:
                eprint("Programa interrumpido...\n Cerrando navegador")
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()

        ####################
        # Reprocesar Precios   
        case 7:
            eprint(f"{n_menu_principal}: Reprocesar Precios para {cantidad_muestras} muestras")
            try:
                from __myLIMS_modulos__  import *
                driver = secuencia_inicio()

                for idx, id_muestra in enumerate(muestras_entrada):
                    try:
                        flag_estado = secuencia_estado_muestra(driver, id_muestra, idx=idx, total=cantidad_muestras, estados=estadoMuestras)
                        if flag_estado == -1: 
                            if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "SALTADA")
                            continue
                        
                        eprint("Seccion de precios")
                        BotonSection(driver,"SectionPrice", log=True, funcion_print=logprint).click()
                        EsperarCARGA_myLIMS(driver)
                            
                        #EDITAR
                        try:
                            #Encontrar elemento con clase control-label y texto moneda de origen
                            control_label = '//div[@class="labsoft-ui-input"]/label[@class="control-label" and contains(text(), "Moneda de Origen")]/ancestor::div[@class="labsoft-ui-input"]'
                            moneda_actual = driver.find_element(By.XPATH, control_label+'//input[@class="k-input" and @role="combobox"]').get_attribute("value")
                            
                            if moneda_actual in ["Peso Mexicano","Unidad de Fomento", "Peso Colombiano"]:
                                boton = BotonAccion(driver, "CalculatePriceButton", log=True, funcion_print=logprint)
                                boton.click()
                                boton.find_element(By.XPATH,"./..//li[@data-test='CalculatePriceButtonItem-RecalculatePrice']").click()

                                BotonVentana(driver,"Confirmar", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver)

                            else:
                                driver.find_element(By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="BackToListButton" and text()="Editar"]').click()
                                logprint("Editando muestra")
                                EsperarCARGA_myLIMS(driver, espera=.5)

                                combobox = driver.find_element(By.XPATH, control_label+'//input[@class="k-input" and @role="combobox"]')
                                n_combobox = combobox.get_attribute("aria-owns")
                                
                                combobox.find_element(By.XPATH, control_label+"//span[contains(@class, 'k-i-arrow-60-down')]").click()
                                logprint(f"click en moneda de origen [{n_combobox}]")
                                EsperarCARGA_myLIMS(driver)

                                if paisActual == "colombia":
                                    driver.find_element(By.XPATH, f"//ul[@role='listbox' and @id='{n_combobox}']/li[contains(text(), 'Peso Colombiano')]").click()
                                    logprint("click en peso colombiano")

                                elif paisActual == "mexico":
                                    driver.find_element(By.XPATH, f"//ul[@role='listbox' and @id='{n_combobox}']/li[contains(text(), 'Peso Mexicano')]").click()
                                    logprint("click en peso mexicano")

                                else:
                                    driver.find_element(By.XPATH, f"//ul[@role='listbox' and @id='{n_combobox}']/li[contains(text(), 'Unidad de Fomento')]").click()
                                    logprint("click en unidad de fomento")
                                
                                EsperarCARGA_myLIMS(driver)
                                BotonAccion(driver, "SaveButton", log=True, funcion_print=logprint ).click()
                                EsperarCARGA_myLIMS(driver, espera=.5)

                                #Esperar alerta
                                if EsperarVentana(driver,segundos=2):
                                    #Revisar que titulo sea "Volver a calcular Precios" y hacer click en Si, caso contrario ignorar
                                    ventana_titulo = driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//span[@class="k-window-title"]').text
                                    if ventana_titulo == "Volver a calcular Precios":
                                        BotonVentana(driver,"Si", log=True, funcion_print=logprint ).click()
                                        
                                    else:    
                                        eprint(f"Otra ventana encontrada [titulo: {ventana_titulo}], saltando muestra...")
                                        if Registrar: 
                                            CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ALERTA PRECIOS")
                                        continue

                        except ElementNotInteractableException:
                            if SaltarMuestra:
                                eprint("No se pudo encontrar el boton de actualizar recipientes, saltando muestra...")
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR PRECIOS")
                                continue
                            
                            else:
                                eprint("No se pudo encontrar el boton de actualizar recipientes...")
                                
                                mylims_ventanas = driver.find_elements(By.XPATH, "//body/div[contains(@class, 'k-window') and contains(@style, 'display: block;')]")
                                cantidad_ventanas = len(mylims_ventanas)
                                logprint(f"Cantidad ventanas: {cantidad_ventanas}")

                                if cantidad_ventanas == 0:
                                    driver.find_element(By.XPATH,"//ul/li[@data-test='CalculatePriceButtonItem-UpdatePrice']").click()
                                    EsperarCARGA_myLIMS(driver)

                                if cantidad_ventanas > 0:
                                    driver.get(myLIMSdomain)
                                    EsperarCARGA_myLIMS(driver)

                                    driver.get(f"{myLIMSdomain}Main.cshtml#Sample/Details/{id_muestra}")
                                    EsperarCARGA_myLIMS(driver)

                        #recorrer hasta llegar al input y hacer click para obtener el aria y el n de combox
                        #buscar por ese combox el li que corresponde a unidad de fomento

                        eprint("Seccion de Recipientes")
                        
                        try:
                            BotonSection(driver,"SectionContainerItem", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver)

                            BotonAccion(driver, "ContainerGenerateButton", log=True, funcion_print=logprint ).click()
                            EsperarCARGA_myLIMS(driver, espera=.5)
                            
                            btn_recreate = driver.find_elements(By.XPATH, "//ul/li[@data-test='RecreateSampleContainersButton' and contains(@style, 'display: list-item;')]")

                            if btn_recreate:
                                btn_recreate[0].click()

                                #Esperar alerta
                                if EsperarVentana(driver,segundos=2):
                                    #Revisar que titulo sea "Volver a calcular Precios" y hacer click en Si, caso contrario ignorar
                                    ventana_titulo = driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//span[@class="k-window-title"]').text
                                    if ventana_titulo == "Recrear Recipientes":
                                        BotonVentana(driver,"Confirmar", log=True, funcion_print=logprint ).click()
                                        
                                    else:    
                                        eprint(f"Otra ventana encontrada [titulo: {ventana_titulo}], saltando muestra...")
                                        if Registrar: 
                                            CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ALERTA PRECIOS")
                                        continue
                                    
                                #Esperar alerta
                                if EsperarVentana(driver,segundos=2):
                                    #Revisar que titulo sea "Volver a calcular Precios" y hacer click en Si, caso contrario ignorar
                                    ventana_titulo = driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//span[@class="k-window-title"]').text
                                    if ventana_titulo == "Atención":
                                        BotonVentana(driver,"Confirmar", log=True, funcion_print=logprint ).click()
                                        
                                    else:    
                                        eprint(f"Otra ventana encontrada [titulo: {ventana_titulo}], saltando muestra...")
                                        if Registrar: 
                                            CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ALERTA PRECIOS")
                                        continue
                            
                                EsperarCARGA_myLIMS(driver)
                                
                            else:
                                driver.find_element(By.XPATH, "//ul/li[@data-test='UpdateSampleContainersButton']").click()

                            EsperarCARGA_myLIMS(driver)

                            # driver.find_element(By.XPATH,"//ul/li[@data-test='RecreateSampleContainersButton']").click()
                            # EsperarCARGA_myLIMS(driver)
                            
                            # driver.find_element(By.XPATH,"//ul/li[@data-test='UpdateSampleContainersButton']").click()
                            # EsperarCARGA_myLIMS(driver)
                            

                        except ElementNotInteractableException:
                            eprint(f"No se pudo encontrar el boton de actualizar recipientes, saltando muestra...")
                            if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR RECIPIENTES")
                            continue

                        #Esperar alerta
                        if EsperarVentana(driver,segundos=2):
                            eprint("Ventana encontrada, saltando muestra...")
                            if Registrar: 
                                CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ALERTA RECIPIENTES")
                            continue

                        if Registrar: 
                            CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "LISTA REPROCESADA")
                            
                        eprint("Muestra actualizada")

                    except BaseException as e:
                        eprint(f"Error para la muestra {id_muestra}:\n\n {FormatoExcepcion(e)}")
                        if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR")
                        notify(title=f"Problemas con la muestra {id_muestra}!", body=type(e).__name__)
                        sleep(3)

                eprint(f"Programa finalizado... Cerrando\n")
                notify(title="Programa finalizado")
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()

            except NoSuchWindowException:
                eprint("Ventana de navegador cerrada")

            except KeyboardInterrupt:
                eprint("Programa interrumpido...\n Cerrando navegador")
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()
        
        ################################################################################################################################################################################################
        # Descargar Muestras en lista
        case 15:
            eprint(f"{n_menu_principal}: Descargar Muestras en lista para {cantidad_muestras} muestras")
            
            try:
                from __myLIMS_modulos__  import *
                try:
                    pais = {
                        "chile":            "SCL",
                        "peru":             "LIM",
                        "colombia":         "BOG",
                        "mexico":           "MTY",
                    }[paisActual]
                    
                    filtros = {
                        "finalizadas":      [f"Muestras finalizadas Hidrolab {pais}"],
                        "metalab":          ["Muestras finalizadas Metalab SCL"],
                        "publicadas":       ["Muestras publicadas Hidrolab SCL"],
                    }[filtroActual]

                    if filtroActual == "metalab":
                        IDbotonesDocumentos = ["1049",    #metalab antiguo
                                            "1217"]   #metalab
                        
                    if filtroActual == "publicadas":
                        IDbotonesDocumentos = ["1120"]   #Análisis

                    if filtroActual == "finalizadas":
                        IDbotonesDocumentos = {
                            "chile"             :   ["1110","1220",            #No ETFA antiguo
                                                    "1112", "1187","1219",     #ETFA antiguo

                                                    "1229", #No ETFA 
                                                    "1228"  #ETFA ACTUAL
                                                    ],

                            "peru"              :   ["1145"],   #Análisis

                            "colombia"          :   ["1233",    #Alimentos
                                                    "1245",    #Canabis
                                                    "1193",    #Aguas Potable
                                                    ],
                                                    
                            "mexico"            :   ["1124"],   #Análisis    
                        }[paisActual]

                    for id in id_etfa_config+id_no_etfa_config:
                        if id not in IDbotonesDocumentos: IDbotonesDocumentos.append( str(id) )

                except KeyError as e:
                    eprint(f"El valor del filtro: {filtroActual} no fue reconocido por el programa (config.txt)\n{e}\n")
                    input("Enter para cerrar...")
                    exit(1)
                
                dir_RUTINA          =   os.path.join(dir_Descargados, "Rutinas")
                dir_CONTROLES       =   os.path.join(dir_Descargados, "Controles")
                dir_AMBOS           =   os.path.join(dir_Descargados, "Ambos")
                dir_OTROS           =   os.path.join(dir_Descargados, "Otros")

                if not os.path.isdir(dir_Descargados): os.mkdir(dir_Descargados)
                if not os.path.isdir(dir_RUTINA): os.mkdir(dir_RUTINA)
                if not os.path.isdir(dir_CONTROLES): os.mkdir(dir_CONTROLES)
                if not os.path.isdir(dir_AMBOS): os.mkdir(dir_AMBOS)
                if not os.path.isdir(dir_OTROS): os.mkdir(dir_OTROS)

                if len([f for f in Path(dir_Descargados).iterdir() if f.is_file()]) != 0:
                    eprint("El directorio de Descarga no está vacío...\n")
                if len(os.listdir(dir_RUTINA)) != 0: 
                    eprint(f"El directorio de Descarga de rutina no está vacío...\n")
                if len(os.listdir(dir_CONTROLES)) != 0: 
                    eprint(f"El directorio de Descarga de controles no está vacío...\n")
                if len(os.listdir(dir_AMBOS)) != 0: 
                    eprint(f"El directorio de Descarga de rutina y controles no está vacío...\n")

                prefs = prefs | { 
                        'download.default_directory' : dir_Descargados,
                        "savefile.default_directory": dir_Descargados,
                }
                DriverOptions.add_experimental_option("prefs",prefs)

                driver = secuencia_inicio()

                MuestrasCantidad = len(muestras_entrada)
                TotalDescarga = 0
                
                if not AutoPublicar: TotalPublicados = "Desactivado"
                else: TotalPublicados = 0

                if not RevisarRutinas: TotalCambioFechas = "Desactivado"
                else: TotalCambioFechas = 0

                for MuestraIndice, id_muestra in enumerate(muestras_entrada,1):
                    try:
                        driver.get(f"{myLIMSdomain}Main.cshtml#Sample/Details/{id_muestra}")
                        EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)
                        
                        N_Muestra = driver.find_element(By.XPATH, '//input[@data-test="ControlNumber"]').get_attribute("value")
                        muestra_estado = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']/div[1]/div[1]//div[5]/div[3]//input[@class='k-input']").get_attribute("value")
                        cliente = driver.find_element(By.XPATH, '//input[@data-bind="value: Account.Identification"]').get_attribute("value")
                        
                        Excepcion_error = ""
                        IntentosDeCarga = 5

                        flagControles = False
                        flagDescargar = False

                        if not SoloBuscarControles:
                            cant_previa = len(os.listdir(dir_Descargados))
                        else:
                            cant_previa = 0
                        
                        if SoloBuscarControles:
                            eprint( f'\nRevisando ID: {id_muestra}\n'+
                                    f'N de Muestra: {N_Muestra}\n'+
                                    f'Muestras Restantes: {MuestrasCantidad-MuestraIndice} Muestras [{MuestraIndice}/{MuestrasCantidad}]\n'+
                                    f'Registradas: {TotalDescarga} - Publicadas: {TotalPublicados} - Cambios de Fechas: {TotalCambioFechas}')
                        else:
                            eprint( f'\nRevisando ID: {id_muestra}\n'+
                                    f'N de Muestra: {N_Muestra}\n'+
                                    f'Muestras Restantes: {MuestrasCantidad-MuestraIndice} Muestras [{MuestraIndice}/{MuestrasCantidad}]\n'+
                                    f'Descargadas: {TotalDescarga} - Publicadas: {TotalPublicados} - Cambios de Fechas: {TotalCambioFechas}')

                        logprint(f"Muestra en estado: {muestra_estado}")

                        BotonSection(driver,"SectionMessage", log=True, funcion_print=logprint ).click()
                        EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)

                        if muestra_estado == "Publicada":
                            if DescargarPublicadas:
                                flagDescargar = True
                                eprint(f"[Publicada para Descargar]")
                            else:
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "YA PUBLICADA")
                                eprint(f"[Ya Publicada]\n")
                                continue

                        #################
                        #Revisar mensajes
                        #Hacer click en k-pager-nav hasta que aparezca k-state-disabled en class?
                        flagCambiarFecha, flagRutina = BuscarAlertas(driver, tipo_rutinas, tipo_horas, funcion_print=eprint)
                        EsperarCARGA_myLIMS(driver)
                        
                        ###################################################
                        #Cambiar Fechas
                        if flagCambiarFecha and not flagDescargar:
                            flagFechasCambiadas = True

                            if not RevisarRutinas: 
                                flagRutina = True
                                flagDescargar = True

                            else:
                                elemento_filtro = driver.find_element(By.XPATH, "//input[@class='select2-search__field' and @placeholder='Filtro del mensaje']")
                                elemento_filtro.click()
                                elemento_filtro.send_keys("tipo:horas")
                                elemento_filtro.send_keys(Keys.ENTER)

                                BotonAccion(driver,"Filtro").click()
                                EsperarCARGA_myLIMS(driver)

                                xpath_mensajes = '//div[@class="myLIMSweb-mail-list-item-box"]//li[contains(@class, "list-group-item")]'
                        
                                lista_alertas = driver.find_elements(By.XPATH, xpath_mensajes)
                                lista_alertas = sorted([f"({xpath_mensajes})[{i+1}]" for i in range(len(lista_alertas))], reverse=True)

                                lista_alertas_pop = []

                                for m_index, iter_xpath in enumerate(lista_alertas):
                                    lista_cambios = []
                                    
                                    mensaje = driver.find_element(By.XPATH, iter_xpath)

                                    m_tipo      = mensaje.find_element(By.XPATH,'./div/div[3]').text.lower()
                                    m_inicio    = mensaje.find_element(By.XPATH,'./div/div[2]/div[1]').text
                                    m_state     = mensaje.get_attribute("class")

                                    if "inactive" in m_state:
                                        lista_alertas_pop.append(m_index)
                                        continue  

                                    if m_tipo in tipo_horas:
                                        eprint("[Alerta de Horas]")
                                        mensaje.click()
                                        EsperarCARGA_myLIMS(driver)

                                        BotonAccion(driver,"Visualizar").click()
                                        EsperarCARGA_myLIMS(driver,extra=1)

                                        iframe = WebDriverWait(driver, 15).until( EC.presence_of_element_located((By.XPATH, '//div[@class="mce-tinymce mce-container mce-panel"]//iframe')) )

                                        driver.switch_to.frame(iframe)

                                        xpath_alertas = "//body[@id='tinymce']//ul/li"
                                        WebDriverWait(driver, 15).until( EC.presence_of_element_located((By.XPATH, xpath_alertas)) )
                                        [lista_cambios.append(_.text) for _ in driver.find_elements(By.XPATH,xpath_alertas)]

                                        driver.switch_to.default_content()

                                        BotonAccion(driver,"Cancelar").click()
                                        
                                        try:

                                            if cliente in ["AGUAS PATAGONIA S.A"]:
                                                inicio_jornada = "6:30"
                                                extension_jornada = "17:29"
                                                __inicio, __fin = FormatoLimiteHoras(inicio_jornada, extension_jornada)

                                                eprint(f"[Cliente {cliente} con fechas especificas inicio {__inicio} y final {__fin}]")
                                            
                                            else:
                                                inicio_jornada = INICIO_JORNADA
                                                extension_jornada = EXTENSION_JORNADA

                                            if CambiarFechas(driver, lista_cambios, inicio_joranda=inicio_jornada, extension_jornada=extension_jornada, funcion_print=logprint):
                                                BotonSection(driver,"SectionMessage").click()
                                                EsperarCARGA_myLIMS(driver)

                                                driver.find_element(By.XPATH, iter_xpath).click()
                                                EsperarCARGA_myLIMS(driver, funcion_print=eprint)

                                                BotonAccion(driver,"Inactivar").click()
                                                EsperarCARGA_myLIMS(driver, funcion_print=eprint)

                                                driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//textarea[@class="k-textbox"]').send_keys("Corregido")
                                                BotonVentana(driver,"Confirmar").click()
                                                EsperarCARGA_myLIMS(driver, funcion_print=eprint)

                                                eprint("[Alerta Horas Procesada]")

                                            else:
                                                eprint("[Problemas con las Horas]")
                                                flagFechasCambiadas = False
                                    
                                        except (ElementClickInterceptedException,ElementNotInteractableException) as e:
                                            raise ExcepcionDeMuestra("Error al cambiar fechas (Reintentar)")
                                
                                else:
                                    
                                    for i in sorted(lista_alertas_pop, reverse=True):
                                        del lista_alertas[i]

                                    if len(lista_alertas) == 0:
                                        eprint("[Sin alertas de Horas]")

                                    else:
                                        if flagFechasCambiadas:
                                            TotalCambioFechas += 1
                                            eprint(f"[Fechas cambiadas]")
                                        else:
                                            flagDescargar = True
                        
                        ###################################################
                        #Revisar Controles Pendientes
                        BotonSection(driver,"SectionRelatedSamples", log=True, funcion_print=logprint ).click()
                        wait(1)
                        EsperarCARGA_myLIMS(driver)
                        
                        cant_controles, lista_controles = ContarControlesPendientes(driver, ID_Actual=id_muestra)
                        
                        if flagRutina:
                            flagDescargar = True
                            lista_controles = ["-"]

                        if cant_controles != 0:
                            eprint(f"[{cant_controles} Controles Pendientes]")
                            logprint(f'controles: {" - ".join(lista_alertas)}')
                            flagDescargar = True
                            flagControles = True
                        else:
                            logprint('Sin controles')

                        ###################################################
                        #Intentar Publicar y continuar
                        if not flagDescargar and not flagControles and muestra_estado != "Publicada":

                            if AutoPublicar:
                                Publicar = MuestraPublicar(driver, id_muestra, url=myLIMSdomain ,kill=True, funcion_print=logprint)

                                if Publicar == "Atraso":
                                    eprint("[Atraso - No Publica]")

                                if Publicar and Publicar != "Atraso":
                                    eprint("[Publica]\n")
                                    
                                    if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "PUBLICADO")
                                        
                                    TotalPublicados += 1
                                    continue

                                if not Publicar and Publicar != "Atraso":
                                    eprint("[No Publica]")

                            else:
                                if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "PARA PUBLICAR")
                                
                                eprint("[Publicable]\n")
                                continue
                        
                        if SoloBuscarControles:
                            if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "PARA DESCARGAR")
                            eprint("[Saltada - Descargable]\n")

                        else:  
                            eprint("[Descarga]\n")
                            BotonSection(driver,"SectionDetails", log=True, funcion_print=logprint ).click()

                            ############################
                            # PROCESADO descargar documento              
                            # USAR N de Muestra para encontrar archivo de muestra actual y moverlo
                            EsperarCLICK(driver,atributo="data-test",valor="DocumentsButton", kill=True)
                            EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)
                            
                            botones = driver.find_element(By.XPATH,'//button[@data-test="DocumentsButton"]/following-sibling::ul').find_elements(By.TAG_NAME,'li')
                            id_botones_myLIMS = [_.get_attribute("data-test").split(":")[1] for _ in botones]

                            obj_botones = 0
                            for boton_id in IDbotonesDocumentos:
                                if boton_id in id_botones_myLIMS:
                                    IDboton = boton_id
                                    obj_botones += 1

                            #Priorizar Aguas Potable frente a otros botones en COLOMBIA
                            if obj_botones >= 2:
                                if "1165" in id_botones_myLIMS:
                                    IDboton = "1165"
                                else:
                                    raise ExcepcionDeCarga(f"No se encontró boton en la lista ({IDbotonesDocumentos}) para descargar documento (ID de botones disponibles en myLIMS: {id_botones_myLIMS})")

                            if obj_botones == 0:
                                raise ExcepcionDeCarga(f"No se encontró boton en la lista ({IDbotonesDocumentos}) para descargar documento (ID de botones disponibles en myLIMS: {id_botones_myLIMS})")
                            
                            EsperarCLICK(driver,atributo="data-test",valor=f"DocumentsButtonItem-DocTemplateId:{IDboton}", kill=True)
                            wait(3)
                            EsperarCARGA_myLIMS(driver, funcion_print=eprint, reintentos=30, kill=True)

                            #Desaparece barra naranja
                            for _ in range(timeout):
                                if queue_redy(driver): break
                                if alerta_visible(driver): raise ExcepcionDeMuestra("ALERTA en procesado de muestra (Reintentar)")
                                wait(1)

                            else:
                                raise ExcepcionDeMuestra("TIMOUT en procesado de muestra (notificacion naranja no desaparece)")
                            wait(1)
                            #Esperar descarga de documento revisando cantidad de archivos en carpeta
                            for _ in range(timeout):
                                if cant_previa == len(os.listdir(dir_Descargados)):
                                    wait(1)
                                    continue
                                
                                if any(".crdownload" in archivo or ".part" in archivo for archivo in os.listdir(dir_Descargados)):
                                    wait(1)
                                    continue

                                if alerta_visible(driver): raise ExcepcionDeMuestra("ERROR en procesado de muestra (Reintentar)")
                                
                                if Registrar: 
                                    CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "ERROR")
                                    
                                TotalDescarga += 1
                                break

                            else:
                                raise ExcepcionDeCarga("No se ha descargado documento (Cantidad de archivos)")

                            if Registrar: CambiarEstadoIDxlsx(dirExcelEntrada, id_muestra, nombre_columnas, "DESCARGA")

                            nombre_informe = ""
                            nombre_informe_nuevo = ""

                            # [296069-2/2025.0] =>[296069][2/2025.0] 
                            N_Muestra, sub_muestra = N_Muestra.split("-")
                            
                            lista_descargas = [str(f) for f in os.listdir(dir_Descargados) if os.path.isfile( os.path.join(dir_Descargados,f) )]

                            for archivo in lista_descargas:
                                # eprint(f"ta {N_Muestra} en {archivo}? => {N_Muestra in archivo} ")
                                if N_Muestra in archivo and "(" not in archivo and ")" not in archivo:
                                    nombre_informe = archivo
                                    n_sub_muestra = sub_muestra.split("/")[0]
                                    
                                    if n_sub_muestra != "1":
                                        #Submuestra , cambiar nombre de archivo por numero
                                        # 296069-2/2025.0 => Informe análisis ETFA para revisión - 296069-1-2025_0.pdf

                                        # 2/2025.0 => 2-2025_0
                                        sub_muestra = sub_muestra.replace("/","-").replace(".","_") 

                                        # Informe análisis ETFA para revisión - 
                                        prefijo = archivo.split(N_Muestra+"-")[0]   

                                        #Informe análisis ETFA para revisión - 296069-2-2025_0.pdf
                                        nombre_informe_nuevo = prefijo+N_Muestra+"-"+sub_muestra+".pdf"
                                    
                                    break

                            else: 
                                raise ExcepcionDeCarga(f"No se encontró el archivo de muestra {N_Muestra} en la carpeta de descarga\n\nLISTA:\n{lista_descargas}")
                            
                            dir_archivo = os.path.join(dir_Descargados,nombre_informe)
                            
                            #MOVER DOCUMENTO DESCARGADO A CARPETA EN FUNCION DE FLAG
                            if not os.path.isfile(os.path.join(dir_archivo)):
                                raise ExcepcionDeCarga(f"El archivo {nombre_informe} no fue encontrado en la carpeta de descarga para clasificarlo")
                            
                            if nombre_informe_nuevo != "":
                                #Cambiar nombre a submuestra para renombrar
                                nombre_informe = nombre_informe_nuevo
                            
                            try:
                                if flagRutina and not flagControles:
                                    os.rename(dir_archivo, os.path.join(dir_RUTINA,nombre_informe))
                                    logprint(f"[RUTINA] Moviendo {dir_archivo} a {os.path.join(dir_RUTINA,nombre_informe)}")
                                
                                elif not flagRutina and flagControles:
                                    os.rename(dir_archivo, os.path.join(dir_CONTROLES,nombre_informe))
                                    logprint(f"[CONTROLES] Moviendo {dir_archivo} a {os.path.join(dir_CONTROLES,nombre_informe)}")
                                
                                elif flagRutina and flagControles:
                                    os.rename(dir_archivo, os.path.join(dir_AMBOS,nombre_informe))
                                    logprint(f"[RUTINA Y CONTROLES] Moviendo {dir_archivo} a {os.path.join(dir_AMBOS,nombre_informe)}")
                                
                                else:
                                    os.rename(dir_archivo, os.path.join(dir_OTROS,nombre_informe))
                                    logprint(f"[OTRO] Moviendo {dir_archivo} a {os.path.join(dir_OTROS,nombre_informe)}")

                            except FileExistsError:
                                eprint(f"El archivo {nombre_informe} ya existe en la carpeta de descarga, dejando en directorio Descargados\n")
                                if dir_archivo != os.path.join(dir_Descargados,nombre_informe):
                                    os.rename(dir_archivo, os.path.join(dir_Descargados,nombre_informe) )


                    #######################
                    # EXCEPCIONES GENERALES
                    except Exception as e:
                        Excepcion_error = e
                        while True:
                            try:
                                requests.head("http://www.google.com/", timeout=5)
                                break
                            except requests.ConnectionError:
                                eprint("No hay connexión a internet, reintentando cada 1 minuto...")
                                wait(60)

                        if isinstance(e, (ExcepcionDeMuestra,UnexpectedAlertPresentException, StaleElementReferenceException) ):
                            eprint(f'__________________\nProblemas con la muestra {id_muestra}\n{FormatoExcepcion(e)}\n')
                        
                        if isinstance(e, (InvalidSessionIdException, ExcepcionDeCarga) ):
                            eprint(f'__________________\nProblemas con la Navegador en la muestra {id_muestra}\n{FormatoExcepcion(e)}\n')
                        
                        if isinstance(e, KeyError):
                            eprint(f'__________________\nProblemas Internos en el proceso\n{FormatoExcepcion(e)}\n')
                        
                        if not isinstance(e, (ExcepcionDeMuestra, UnexpectedAlertPresentException, StaleElementReferenceException, InvalidSessionIdException, ExcepcionDeCarga, KeyError) ):
                            eprint(f'__________________\nProblemas desconocidos con la muestra {id_muestra}\n{FormatoExcepcion(e)}\n')
                        
                        wait(1)
                        driver.refresh()
                        EsperarCARGA_myLIMS(driver, funcion_print=eprint)
                        IntentosDeCarga -= 1
                        eprint(f'REINTENTANDO [{IntentosDeCarga} Intentos restantes]\n')
                        continue
                    
                    except BaseException as e:
                        eprint(f"Error para la muestra {id_muestra}:\n\n {FormatoExcepcion(e)}")
                        notify(title=f"Problemas con la muestra {id_muestra}!", body=type(e).__name__)
                        sleep(3)
                        break
                    

                eprint(f"Programa finalizado... Cerrando\n")
                notify(title="Programa finalizado")
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()

            except NoSuchWindowException:
                eprint("Ventana de navegador cerrada")

            except KeyboardInterrupt:
                eprint("Programa interrumpido...\n Cerrando navegador")
                try:
                    Logout(driver,logout_url=Labsoftdomain)
                    driver.quit()
                except NameError:
                    pass

        ####################
        # Abrir Directorio de descarga 
        case 17:
            eprint(f"{n_menu_principal}: Abrir directorio con muestras descargadas")
            
            #crear el directorio si no existe
            if not os.path.isdir(dir_Descargados):
                eprint(f"El directorio de Descargas no existe, creando {dir_Descargados}")
                os.mkdir(dir_Descargados)

            os.system(f"start explorer.exe \"{dir_Descargados}\"")

        ####################
        # Abrir excel con lista de muestras [RUTINAS]
        case 18:
            eprint(f"{n_menu_principal}: Abrir excel con lista de muestras")

            while ComprobarExcelAbierto(dirExcelEntrada,colnames=nombre_columnas):
                eprint("Error de permisos, excel abierto")
                messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")
                
            os.system(f"start {app_excel} \"{dirExcelEntrada}\"") 
            
        ####################
        # Limpiar EXCEL de lista de muestras    
        case 19:
            eprint(f"{n_menu_principal}: Limpiar excel con muestras para {cantidad_muestras} muestras")

            while ComprobarExcelAbierto(dirExcelEntrada,colnames=nombre_columnas):
                eprint("Error de permisos, excel abierto")
                messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")

            ReestablecerXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas)
            muestras_entrada = pd.read_excel(dirExcelEntrada)["ID MUESTRAS"].to_list()
            cantidad_muestras = len(muestras_entrada)

        ####################
        # Abrir EXCEL en RegistrosPendientes [CONTROLES]    
        case 20:
            eprint(f"{n_menu_principal}: Abrir excel de RegistrosPendientes [RegistroAuxiliar]")
            while ComprobarExcelAbierto(dirExcelAuxiliar,colnames=nombre_columnas_id):
                eprint("Error de permisos, excel abierto")
                messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")

            os.system(f"start {app_excel} \"{dirExcelAuxiliar}\"")

        ####################
        # Abrir EXCEL en DescargaMuestras [ESTADOS]    
        case 21:
            eprint(f"{n_menu_principal}: Abrir excel con lista de Estados [Registro]")

            while ComprobarExcelAbierto(dirExcelEstados,colnames=nombre_columnas_reg):
                eprint("Error de permisos, excel abierto")
                messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")

            os.system(f"start {app_excel} \"{dirExcelEstados}\"")     

        ####################
        # Mover Registro DescargaMuestras a historico
        case 22:
            eprint(f"{n_menu_principal}: Mover Excel Descarga Muestras a historico para {cantidad_muestras} muestras")

            while ComprobarExcelAbierto(dirExcelEstados,colnames=nombre_columnas_reg):
                eprint("Error de permisos, excel abierto")
                messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")
            
            while ComprobarExcelAbierto(dirExcelHistorico,colnames=nombre_columnas_id):
                eprint("Error de permisos, excel abierto")
                messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")

            #Obtener ID de historico y estados, borrar duplicados y usar solo ID que sean numeros
            lista_excel = list(set( ListaMuestraXLSX(dirExcel=dirExcelEstados, colname=nombre_columnas_reg[1], colnames=nombre_columnas_reg) + ListaMuestraXLSX(dirExcel=dirExcelHistorico, colname=nombre_columnas_id[0], colnames=nombre_columnas_id) ))
            
            ReestablecerXLSX(dirExcelHistorico, colnames=nombre_columnas_id, filtro=True)
            # ReestablecerXLSX(dirExcelEstados, colnames=nombre_columnas_reg, filtro=True)

            ListaAColumnaXLSX(dirExcelHistorico, valores_fila=lista_excel ,colnames=nombre_columnas_id, colname=nombre_columnas_id[0], funcion_print=logprint)

        ################################################################################################################################################################################################
        # Recargar muestras en lista 
        case 30:
            eprint(f"{n_menu_principal}: Recargar muestras en lista para {cantidad_muestras} muestras")
            
            while ComprobarExcelAbierto(dirExcelEntrada,colnames=nombre_columnas):
                eprint("Error de permisos, excel abierto")
                messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")

            muestras_entrada = pd.read_excel(dirExcelEntrada)["ID MUESTRAS"].to_list()
            cantidad_muestras = len(muestras_entrada)

        ################################################################################################################################################################################################
        # Salir
        case 31:
            eprint(f"{n_menu_principal}: Programa Terminado")
            sleep(1)
            exit(0)

        case -10:
            eprint(f"{n_menu_principal}: Boton temporal")
        
        case -1:
            eprint(f"{n_menu_principal}: Programa Terminado")
            sleep(1)
            exit(0)
