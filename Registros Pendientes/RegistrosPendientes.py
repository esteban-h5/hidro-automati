try:
    from selenium.webdriver.common.alert import Alert
    from tkinter import messagebox
    from datetime import datetime
    import subprocess, os, sys, shutil
except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)
    
file_name           =   os.path.basename(__file__)
RP_wd               =   os.path.dirname(os.path.realpath(__file__))
internal_lib        =   os.path.normpath(os.path.join(RP_wd,"..","internal_lib"))

sys.path.insert(0, internal_lib)

from __myLIMS_modulos__     import *
from __myLIMS_wrappers__    import *
from __ficheros_modulos__   import *

########################################
#Inicialización de Config
########################################

config              =   GetConfig( dirConfig=os.path.join(RP_wd,"config.txt") )
global_config       =   GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )

try:
    myLIMSdomain        =   global_config["myLIMSdomain"]
    Labsoftdomain       =   global_config["Labsoftdomain"]
    mainUrl             =   f"{myLIMSdomain}Main.cshtml#Sample/SearchBarCode/List"

    app_excel           =   global_config["AppExcel"]

    pais                =   global_config["paisActual"].replace("é","e").replace("ú","u").lower()
    log                 =   global_config["ActivarLOG"]
    
    tipo_rutinas        =   global_config["ListaMensajesRutina"].lower().split(",")
    tipo_horas          =   global_config["ListaMensajesHoras"].lower().split(",")
    
    nombreLOG           =   os.path.join(RP_wd,"log",datetime.now().strftime('reporte_%Y_%m_%d-%H_%M'))

    Publicar            =   config["Publicar"]
    RevisarRutina       =   config["RevisarRutinas"]

    nombreExcelSalida   =   config["nombreExcelSalida"]
    dirExcelSalida      =   os.path.join(RP_wd, nombreExcelSalida)

    nombreExcelEntrada  =   config["nombreExcelEntrada"]
    dirExcelEntrada     =   os.path.join(RP_wd, nombreExcelEntrada)

    nombreExcepciones   =   global_config["nombreExcelExcepciones"]
    dirExcepciones      =   os.path.join(internal_lib, nombreExcepciones)

    nombreExcelError    =   config["nombreExcelError"]
    dirExcelError       =   os.path.join(RP_wd, nombreExcelError)

    delimiter           =   "#######################"
    nombre_columnas     =   ["INDICE MUESTRA","N MUESTRA","ID MUESTRAS","CONTROL CQ PENDIENTE","ID DEL CQ","NUMERO CQ","ESTADO CQ","ACTIVO","CLIENTE","ÁREA DE SERVICIO"]
    nombre_columnas_aux =   ["ID MUESTRAS"]
    
except KeyError as e:
    input(f"Error en archivo de configuración, falta el valor de {e}\n\nEnter para cerrar...")
    exit(1)

if log:
    print("Historial de log activo\n")
    
    if not os.path.isdir( os.path.join(RP_wd,"log") ): os.mkdir(os.path.join(RP_wd,"log"))

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

if Publicar:
    eprint("Publicación activada\n")
else:
    eprint("Publicación desactivada\n")

eprint(f"País Actual: {pais}\n")

tkMenu      =   lambda x1, x2=0, x3=0: subprocess.run(["python", f"{internal_lib}\\__display_modulos__.py","1",str(x1),str(x2),str(x3)], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout
ptkMenu      =   lambda x1, x2=0, x3=0: eprint(f"python \"{internal_lib}\\__display_modulos__.py\" 1 \"{str(x1)}\" \"{str(x2)}\" \"{str(x3)}\"")

tkError     =   lambda msg: [eprint("Mensaje de ERRORs a la espera de interacción...\n"), messagebox.showerror(title="ERROR",message=str(msg))]
tkAlerta    =   lambda msg: [eprint("Alerta a la espera de interacción...\n"), messagebox.showwarning(title="Alerta",message=str(msg))]
tkMensaje   =   lambda msg: [eprint("Mensaje a la espera de interacción...\n"), messagebox.showinfo(title="Información",message=str(msg))]

try:
    MuestraPais = {
        "chile": ["Hidrolab SCL", "Metalab SCL"],
        "peru": ["Hidrolab LIM"],
        "colombia": ["Hidrolab BOG"],
        "mexico": ["Hidrolab MTY"]
    }[pais]

except KeyError:
    eprint(f"El valor pais: {pais} no fue reconocido por el programa (config.txt)\n")
    input("Enter para cerrar...")
    exit(1)

eprint("Iniciando navegador\n")

if not existe_param_env(internal_lib):
    input(f'No se encontró archivo con credenciales. (Param.env)\n\nEnter para cerrar...')
    exit(1)

prefs = prefs | {}
DriverOptions.add_experimental_option("prefs",prefs)
DriverOptions.add_argument("--mute-audio")

driver = Chrome(options=DriverOptions)
id_main_driver = driver.current_window_handle

eprint("Iniciando sesión en myLIMS\n")

try:
    Login(driver, path_internal=internal_lib, post_url=mainUrl, login_url=Labsoftdomain)
    EsperarCARGA_myLIMS(driver)

except ExcepcionDeCarga as e:
    eprint(f"{e}\n")
    input("Enter para cerrar...")
    exit(1)

ListaMuestras = []; ListaMuestrasID = []
ErrorLinks = []

Excepciones              = unique(ListaMuestraXLSX(dirExcel=dirExcepciones, colname="ID MUESTRAS", colnames=nombre_columnas_aux, except_alert=False, except_create=True))
MuestrasRegistradasExcel = unique(ListaMuestraXLSX(dirExcel=dirExcelSalida, colname="ID MUESTRAS", colnames=nombre_columnas, except_alert=False, except_create=True))
listaExcel               = unique(ListaMuestraXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas, colname="ID MUESTRAS", except_kill=False, except_create=True))

try:
    while True:

        eprint(f"Menú principal a la espera...\n")
        slog()

        try:
            Opcion = int(tkMenu(pais, len(ListaMuestras), len(listaExcel)))

        except ValueError as e:
            input(f"Error en el menú: {str(tkMenu(len(ListaMuestras)))} \nExcepcion: {e}")
            Opcion = -2

        match Opcion:

            #Enlistar Muestras
            case 1:
                lista_muestras = SampleRecon(driver, Excluido=MuestrasRegistradasExcel, CentroServicio=MuestraPais, funcion_print=eprint)
                largo_lista_muestras = len(lista_muestras)

                for idx,Muestra in enumerate(lista_muestras):
                    
                    if Muestra["INDICE"] in ListaMuestrasID:
                        eprint(f'Muestra {Muestra["INDICE"]} ya enlistada\n')
                    elif Muestra["INDICE"] in MuestrasRegistradasExcel:
                        eprint(f'Muestra {Muestra["INDICE"]} ya en excel\n')
                    elif Muestra["INDICE"] in Excepciones:
                        eprint(f'Muestra {Muestra["INDICE"]} como excepción\n')

                    else:
                        ListaMuestrasID.append(Muestra["INDICE"])
                        ListaMuestras.append(Muestra)

                if len(ListaMuestras)==0:
                    eprint("No existen Muestras pendientes en navegador\n")
                    tkAlerta("No existen Muestras pendientes en navegador\n")

                else:
                    eprint(f'Lista con {len(ListaMuestras)} muestras finalizadas\n\nYa se puede borrar el Grid\n')
                    tkMensaje(f'Lista con {len(ListaMuestras)} muestras finalizadas\n')
                    state_subp = 1
            
            #Controles Buscar
            case 2:
                cantMPublicadas = 0; cantMPendientes = 0; cantCQPendientes = 0; cantMErrores = 0; cantMAtrasadas = 0

                try:
                    eprint("Reestableciendo sesión en nuevo navegador\n")
                    
                    driver.switch_to.new_window('window')

                    driver.get(myLIMSdomain)

                    restante = len(ListaMuestras)
                    total = restante

                    [driver.add_cookie(_) for _ in driver.get_cookies()]

                    driver.get(myLIMSdomain+"Main.cshtml#WorkSpace")
                    eprint("Esperando carga myLIMS")

                    EsperarCARGA_myLIMS(driver)
                    for Muestra in ListaMuestras:
                        try:
                            ListaActualCQ = []
                            url_muestra = f"{myLIMSdomain}Main.cshtml#Sample/Details/{str(Muestra['ID'])}"

                            eprint(f'\nAbriendo muestra {Muestra["ID"]} ({total - restante + 1} de {total})\n')

                            driver.get(url_muestra)
                            EsperarCARGA_myLIMS(driver)

                            #################################
                            #Revisar si muestra tiene alertas
                            BotonSection(driver,"SectionMessage").click()
                            EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)

                            flagAlerta = False
                            flagCambiarFecha = False

                            #################
                            #Revisar mensajes
                            #Hacer click en k-pager-nav hasta que aparezca k-state-disabled en class
                            flagCambiarFecha, flagAlerta = BuscarAlertas(driver, tipo_rutinas, tipo_horas, funcion_print=eprint)

                            if flagCambiarFecha: flagAlerta = True

                            BotonSection(driver,"SectionRelatedSamples").click()
                            EsperarCARGA_myLIMS(driver)

                            ###################################################
                            #Revisar Controles Pendientes
                            cant_controles, lista_controles = ContarControlesPendientes(driver, ID_Actual=Muestra["ID"])

                            if cant_controles == 0:
                                BotonSection(driver,"SectionDetails").click()
                                EsperarCARGA_myLIMS(driver)
                                
                                if flagAlerta:
                                    eprint("Muestra con alertas")
                                
                                if not RevisarRutina:
                                    if Publicar:
                                        Publicado = MuestraPublicar(driver, ID_Muestra=Muestra["ID"], kill=True, url=myLIMSdomain, funcion_print=logprint)

                                        if Publicado == "Atraso":
                                            eprint("Muestra Atrasada")
                                            
                                            fila_muestra = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"], Muestra["CLIENTE"], "ATRASO", "ATRASO", "ATRASO", Muestra["ESTADO"], Muestra["ACTIVO"], Muestra["AREA"]]
                                            FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fila_muestra, colnames=nombre_columnas, except_kill=False, except_create=True)                                    
                                            
                                            cantMAtrasadas += 1; cantMPendientes += 1
                                            continue

                                        if Publicado and Publicado != "Atraso":
                                            eprint("Publicada, saltando revisión de controles")
                                            cantMPublicadas += 1
                                            continue
                                    
                                    if not Publicar:
                                        fila_muestra = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"],"PUBLICABLE", "PUBLICABLE", "PUBLICABLE", Muestra["ESTADO"], Muestra["ACTIVO"], Muestra["CLIENTE"], Muestra["AREA"]]
                                        FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fila_muestra, colnames=nombre_columnas, except_kill=False, except_create=True)                                    
                                
                                        eprint(f"Muestra {str(Muestra['ID'])} sin controles y publicación desactivada")
                                        
                                    cantMPublicadas += 1
                                    continue

                                if RevisarRutina:
                                    if flagAlerta:
                                        eprint("Saltando publicacion y registrando muestra con alertas")
                                        fila_muestra = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"], "ALERTAS", "ALERTAS", "ALERTAS", Muestra["ESTADO"], Muestra["ACTIVO"], Muestra["CLIENTE"], Muestra["AREA"]]
                                        FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fila_muestra, colnames=nombre_columnas, except_kill=False, except_create=True)                                    
                                        
                                        cantMPendientes += 1
                                        continue

                                    else:
                                        if Publicar:
                                            Publicado = MuestraPublicar(driver, ID_Muestra=Muestra["ID"], kill=True, url=myLIMSdomain, funcion_print=logprint)

                                            if Publicado == "Atraso":
                                                eprint("Muestra Atrasada")
                                                
                                                fila_muestra = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"], Muestra["CLIENTE"], "ATRASO", "ATRASO", "ATRASO", Muestra["ESTADO"], Muestra["ACTIVO"], Muestra["AREA"]]
                                                FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fila_muestra, colnames=nombre_columnas, except_kill=False, except_create=True)                                    
                                                
                                                cantMAtrasadas += 1; cantMPendientes += 1
                                                continue

                                            if Publicado and Publicado != "Atraso":
                                                eprint("Publicada, saltando revisión de controles")
                                                cantMPublicadas += 1
                                                continue
                                        
                                        if not Publicar:

                                            fila_muestra = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"],"PUBLICABLE", "PUBLICABLE", "PUBLICABLE", Muestra["ESTADO"], Muestra["ACTIVO"], Muestra["CLIENTE"], Muestra["AREA"]]
                                            FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fila_muestra, colnames=nombre_columnas, except_kill=False, except_create=True)                                    
                                    
                                            eprint(f"Muestra {str(Muestra['ID'])} sin controles y publicación desactivada, saltando revisión de controles")
                                            
                                    cantMPublicadas += 1
                                    continue
                            
                            else:
                                ListaActualCQ = ControlRecon(driver, Muestra["ID"])                                            
                                
                                if len(ListaActualCQ) == 0:
                                    fila_muestra = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"],"PUBLICABLE", "PUBLICABLE", "PUBLICABLE", Muestra["ESTADO"], Muestra["ACTIVO"], Muestra["CLIENTE"], Muestra["AREA"]]
                                    FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fila_muestra, colnames=nombre_columnas, except_kill=False, except_create=True)                                    
                                    
                                    eprint(f"Muestra {str(Muestra['ID'])} se puede publicar")

                                else:
                                    eprint(f'Existen {len(ListaActualCQ)} control(es) de calidad pendiente(s)')

                                    for Control in ListaActualCQ:
                                        
                                        if Control["NOMBRE"] == Muestra["TIPO"]:
                                            eprint(f'Submuestra ID: {Control["ID"]}, saltando...')
                                            continue

                                        cantCQPendientes += 1
                                        fila_control = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"], Control["NOMBRE"], Control["ID"], Control["NUMERO"], Control["ESTADO"], Muestra["ACTIVO"], Muestra["CLIENTE"], Muestra["AREA"]] 
                                        FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fila_control, colnames=nombre_columnas, except_kill=False, except_create=True)                                    

                                cantMPendientes += 1

                        except UnexpectedAlertPresentException:
                            eprint(f'Alerta Presente')
                            Alert(driver).accept()

                            raise ExcepcionDeMuestra("Alerta Presente")
                        
                        except Exception as e:
                            notify(title=f"Problemas con la muestra {Muestra['ID']}!", body=type(e).__name__)

                            eprint(f'##############\nProblemas con la muestra {Muestra["ID"]}\n##############\n\n{FormatoExcepcion(e)}')
                            
                            fila_error = [ Muestra["INDICE"], Muestra["NUMERO"], Muestra["ID"], f"ERROR: {FormatoExcepcion(e)}", "ERROR", "ERROR", "ERROR", Muestra["ACTIVO"], Muestra["CLIENTE"], Muestra["AREA"]]
                            FilaAgregarXLSX(dirExcel=dirExcelError, valores_fila=fila_error, colnames=nombre_columnas, except_kill=False, except_create=True)                                    

                            ErrorLinks.append(myLIMSdomain+"Main.cshtml#Sample/Details/"+Muestra["ID"])
                            eprint("Agregando muestra como error para revisar")

                            restante -= 1; cantMErrores +=1; cantMPendientes += 1
                            continue

                        finally:
                            restante -= 1

                    #Iteración por cada muestra 
                    
                finally:
                    notify(title="Programa finalizado")
                    driver.close()
                    driver.switch_to.window(id_main_driver)

                    fin_de_ciclo=[datetime.now().strftime('[%d-%m-%Y %H:%M]')]+[delimiter for _ in range(len(nombre_columnas)-1)] 
                    FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=fin_de_ciclo, colnames=nombre_columnas, except_kill=False, except_create=True)

                    eprint(
                        f'Se terminó la busqueda\n\n{cantMPublicadas} Muestras Publicadas\n'+
                        f'{cantMPendientes} Muestras Pendientes\n{cantCQPendientes} Controles pendientes\n'+
                        f'{cantMAtrasadas} Muestras Atrasadas\n{cantMErrores} Errores en Muestra\n')

                    # if len(ErrorLinks) != 0: [eprint(_) for _ in ErrorLinks]
                    
                    eprint(f'\nGuardando total de muestras pendientes: {len(ListaMuestras)}\n')
                    ListaMuestras = []; ListaMuestrasID = []

            #Borrar lista Enlistada 
            case 3:
                ListaMuestras = []; ListaMuestrasID = []

                tkMensaje("Lista de muestras pendientes actuales y publicadas Borrada")
                eprint("Lista pendiente y actual Borrada\n")

            #Mostrar datos Actuales
            case 4:
                pass
                # mensaje = ""
                # nMuestras = driver.find_element(By.CLASS_NAME, "k-pager-info").text

                # if nMuestras != "Nada a enseñar.":
                #     nMuestras = int(nMuestras.split("de")[1].split(" ")[1])
                #     mensaje = mensaje+f'Se encuentra(n) {nMuestras} muestra(s) en el driver\n'
                #     eprint(f'Se encuentra(n) {nMuestras} muestra(s) en el driver\n\nLista actual:')
                #     [eprint(f'{_}') for _ in ListaMuestras]; eprint()
                # else:
                #     nMuestras = 0
                #     eprint("No existen muestras en navegador\n")
                #     mensaje = mensaje+"No existen muestras en navegador\n"

                # if len(MuestrasRegistradasExcel) != 0:
                #     mensaje = mensaje + f'Existen {len(MuestrasRegistradasExcel)} muestras guardadas en excel'
                # else:
                #     mensaje = mensaje + f'No existen muestras guardadas en excel'

                # tkMensaje(mensaje)
                    
            ################
            #Registro en txt
            ######

            #Recargar Muestras en Excel
            ################
            case 6:
                Excepciones              = unique(ListaMuestraXLSX(dirExcel=dirExcepciones, colname="ID MUESTRAS", colnames=nombre_columnas_aux, except_alert=False, except_create=True))
                MuestrasRegistradasExcel = unique(ListaMuestraXLSX(dirExcel=dirExcelSalida, colname="ID MUESTRAS", colnames=nombre_columnas, except_alert=False, except_create=True))
                listaExcel               = unique(ListaMuestraXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas, colname="ID MUESTRAS", except_kill=False, except_create=True))

                # listaExcel = ListaMuestraXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas_aux, colname="ID MUESTRAS", except_kill=False, except_create=True)
                # if len(listaExcel) == 0: 
                #     eprint(f'Archivo {nombreExcelEntrada} vacío\n')
                #     catArchivo = "Archivo de registro vacío"
                # else: 
                #     eprint(f'ARCHIVO:\n=>{listaExcel}\n')
                #     catArchivo = f'{len(listaExcel)} muestras dentro de archivo.'

                # eprint(f'NAVEGADOR:\n=>{[_["ID"] for _ in ListaMuestras if _ not in listaExcel]}\n')

                # tkMensaje(f'{catArchivo}\n{len([_["ID"] for _ in ListaMuestras if _ not in listaExcel])} muestras en navegador')
            
            #Exportar navegador a archivo
            ################
            case 7:
                listaExcel = unique(ListaMuestraXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas, colname="ID MUESTRAS", except_kill=False, except_create=True))
                cant_muestras_excel = len(listaExcel)
                
                if cant_muestras_excel != 0:
                    tkAlerta("Archivo RegistroAuxiliar contiene muestras guardadas, concatenando muestras de navegador a archivo")    

                for sample in ListaMuestras:
                    sampleID = sample["ID"]
                    if sampleID in listaExcel:
                        eprint(f'Muestra {sampleID} ya en archivo auxiliar, saltando...')
                    else:
                        AgregarMuestraXLSX(dirExcel=dirExcelEntrada, ID_Muestra=sampleID, colnames=nombre_columnas_aux, except_kill=False, except_create=False)
            
                listaExcel = unique(ListaMuestraXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas, colname="ID MUESTRAS", except_kill=False, except_create=True))
                eprint(
                    f'\nArchivo con {len(listaExcel)} datos\nPrograma con '+
                    f'{len(ListaMuestras)} Muestras\n\nMenú registro archivos a la espera\n')
                
                # eprint(f"Exportando lista a archivo {nombreExcelEntrada}\n")
            
            #Importar desde archivo a navegador       
            ################
            case 8:
                # Alertar registro auxiliar no vacio
                # 
                listaExcel = unique(ListaMuestraXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas, colname="ID MUESTRAS", except_kill=False, except_create=True),invertido=True)
                if driver.current_url == myLIMSdomain+"Main.cshtml#Sample/SearchBarCode/List":
                    if not listaExcel:
                        eprint("Lista de Fichero Vacía")
                        tkAlerta("Lista de Ficheros Vacía")

                    else:
                        eprint("Subiendo Fichero\n")
                        SubirLista(driver,listaExcel, funcion_print=eprint)

                        notify(title="Subida de muestras", body=f"{len(listaExcel)} muestras subidas al navegador")
                        eprint("Grid actualizado\n")
                        tkMensaje("Grid actualizado, muestras agregadas")

                else:
                    eprint("Driver actual no se encuentra en URL para Códigos de Barras\n")

            #Abrir Excel
            ################
            case 9:
                eprint("Abriendo archivo excel auxiliar\n")

                while ComprobarExcelAbierto(dirExcelEntrada,colnames=nombre_columnas_aux):
                    eprint("Error de permisos, excel abierto")
                    messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")
    
                os.system(f"start {app_excel} \"{dirExcelEntrada}\"")

            #Reestablecer Excel
            ################
            case 10:
                ReestablecerXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas_aux)

                listaExcel = unique(ListaMuestraXLSX(dirExcel=dirExcelEntrada, colname=nombre_columnas_aux, colnames=nombre_columnas, except_kill=False, except_create=True))
                eprint(
                    f'Archivo con {len(listaExcel)} datos\nPrograma con '+
                    f'{len(ListaMuestras)} Muestras\n\nMenú registro archivos a la espera\n')           
            
            #Abrir Excel
            case 12:
                eprint("Abriendo archivo excel de muestras\n")

                while ComprobarExcelAbierto(dirExcelSalida, colnames=nombre_columnas):
                    eprint("Error de permisos, excel abierto")
                    messagebox.showerror(title="Error de permisos", message="Se abrio el archivo de muestras con otra aplicación, favor cerrar para continuar")

                os.system(f"start {app_excel} \"{dirExcelSalida}\"")

            #Limpiar Excel
            case 13:
                ReestablecerXLSX(dirExcel=dirExcelSalida, colnames=nombre_columnas)
                Excepciones              = unique(ListaMuestraXLSX(dirExcel=dirExcepciones, colname="ID MUESTRAS", colnames=nombre_columnas_aux, except_alert=False, except_create=True))
                MuestrasRegistradasExcel = unique(ListaMuestraXLSX(dirExcel=dirExcelSalida, colname="ID MUESTRAS", colnames=nombre_columnas, except_alert=False, except_create=True))
                listaExcel               = unique(ListaMuestraXLSX(dirExcel=dirExcelEntrada, colnames=nombre_columnas, colname="ID MUESTRAS", except_kill=False, except_create=True))

            #Cerrar sesión
            case 14:
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()
                break

            #Menu excepción
            case -1:
                eprint("Favor de salir cerrando la sesión\n")


except NoSuchElementException as e:
    input(f'ERROR: No se encontró un elemento, se ha caido la ejecución\n{FormatoExcepcion(e)}\n\nEnter para cerrar')

    Logout(driver,logout_url=Labsoftdomain)
    driver.quit()

    eprint("Terminado\n")
    exit(1)

except TimeoutException as e:  

    eprint(f'ERROR: Carga demorosa, se excedió el timeout')
    Logout(driver,logout_url=Labsoftdomain)
    driver.quit()

    eprint("Mostrando Excepción:")
    eprint(f'{e}')
    exit(1)

except Exception as e:
    
    eprint(f'ERROR: Se cayó la sección del menú\n{FormatoExcepcion(e)}')
    input("Presione enter para terminar\n")
    Logout(driver,logout_url=Labsoftdomain)
    driver.quit()

finally:
    eprint("Terminado\n")
    exit(0)

