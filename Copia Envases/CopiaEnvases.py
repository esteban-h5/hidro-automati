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

CE_wd               =   os.path.dirname(os.path.realpath(__file__))
internal_lib        =   os.path.normpath(os.path.join(CE_wd,"..","internal_lib"))
sys.path.insert(0, internal_lib)

from __myLIMS_modulos__ import (
    GetConfig, MensajeInicial, version_actual, existe_param_env,
    EsperarCARGA_myLIMS, ExcepcionDeCarga, 
    BotonSection, BotonAccion, BotonVentana,
    FormatoExcepcion, ExcepcionDeMuestra,
    UnexpectedAlertPresentException, StaleElementReferenceException, 
    InvalidSessionIdException, NoSuchWindowException, 
    By, EC, DriverOptions, Chrome, Keys, WebDriverWait, DeltaTimer,
    notify, sleep, datetime, requests, prefs, del_alertas_iniciales, pd
)
from __myLIMS_wrappers__ import (
    unique, Cortar,
)

from __ficheros_modulos__ import (
    ListaMuestraXLSX,
    FilaAgregarXLSX,
    AbrirXLSX, 
)

from __myLIMS_wrappers__ import (
    Logout, Login, GetTablaColumna,
    DeltaTimer,
)

########################################
#Inicialización de Config
########################################

config              =   GetConfig( dirConfig=os.path.join(CE_wd,"config.txt") )
global_config       =   GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )

keys_used = [
    "RevisarEtapaActual",
    "ExcluirExcelSalida",
    "CopiarMuestras",
    "CrearPE",
    "SufijoTituloGeneral",
    "nombreExcelEntrada",
    "nombreExcelSalida",
]

keys_used_g = [
    "myLIMSdomain",
    "Labsoftdomain",
    "paisActual",
    "ActivarLOG",
    "AppExcel",
]

for key in keys_used:
    if key not in config.keys():
        input(f"Valor de config \'{key}\' no encontrado en archivo config, enter para continuar igualmente...")
for key in keys_used_g:
    if key not in global_config.keys():
        input(f"Valor de config \'{key}\' no encontrado en archivo global_config, enter para continuar igualmente...")

myLIMSdomain            =   global_config.get("myLIMSdomain")
Labsoftdomain           =   global_config.get("Labsoftdomain")

paisActual              =   global_config.get("paisActual", "").replace("é","e").replace("ú","u").lower()
log                     =   global_config.get("ActivarLOG")
app_excel               =   global_config.get("AppExcel")

RevisarEtapaActual      =   config.get("RevisarEtapaActual")
ExcluirExcelSalida      =   config.get("ExcluirExcelSalida")
CopiarMuestras          =   config.get("CopiarMuestras")
CrearPE                 =   config.get("CrearPE")
SufijoTituloGeneral            =   config.get("SufijoTituloGeneral")

timeout                 =   120

nombre_columnas_in      =   ["ID COTI", "ID MUESTRA", "N COPIAS", "FECHA EJECUCIÓN", "SUFIJO TÍTULO", "AGRUPACIÓN"]
nombre_columnas_out     =   ["INDICE", "ID COTI", "ID MUESTRA INICIAL", "ID COPIA", "PE ID", "PE ACTIVIDAD", "PE LUGAR ID", "ESTADO"]

nombreLOG               =   os.path.join(CE_wd, "log", datetime.now().strftime('reporte_%Y_%m_%d-%H_%M'))

nombreExcelEntrada      =   config.get("nombreExcelEntrada")
dirExcelEntrada         =   os.path.join(CE_wd, nombreExcelEntrada)

nombreExcelSalida       =   config.get("nombreExcelSalida")
dirExcelSalida          =   os.path.join(CE_wd, nombreExcelSalida)

if log:
    print("Historial de log activo\n")

    if not os.path.isdir( os.path.join(CE_wd,"log") ): os.mkdir(os.path.join(CE_wd,"log"))

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
    slog = lambda: None

MensajeInicial(file_name, funcion_print=eprint, config=config, global_config=global_config, funcion_log=logprint )

eprint(f"País Actual: {paisActual}")

if not existe_param_env(internal_lib):
    eprint("Error No se encontró archivo con credenciales. (Param.env)")
    input("Enter para cerrar..")
    exit(1)

xpath_ventana           = "//div[contains(@class,'k-window') and contains(@style,'display: block;')]"
xpath_muestra_activa    = "//div[@id='InterfaceContent']/div[1]//div[@class='labsoft-ui-input checkbox']//input[@data-test='Active']"
xpath_seccion_muestras  = "//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']//div[contains(@class, 'k-auto-scrollable')]"
xpath_estado_muestra    = "//div[@id='InterfaceContent']/div[1]//label[contains(text(),'Estatus de la Muestra')]/following-sibling::span[contains(@class, 'k-combobox')]/span/input[@role='combobox']"
xpath_lista_analitos    = "//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody"
xpath_alerta_inactiva   = f"{xpath_ventana}//span[@class='k-window-title' and contains(text(), 'Registro Inactivo')]/ancestor::div[contains(@class,'k-window') and contains(@style,'display: block;')]"
xpath_ventana_copia     = f"{xpath_ventana}//span[@class='k-window-title' and contains(text(), 'Copiar')]/ancestor::div[contains(@class,'k-window')]"
xpath_sec_muestra       = "//div[@id='InterfaceContent']/div[not(contains(@style, 'display: block;'))]//div[@data-role='grid']"

df_entrada = AbrirXLSX(dirExcelEntrada, colnames=nombre_columnas_in)

if df_entrada.empty:
    input("Sin datos, Enter para cerrar...")

try:
    df_entrada["N COPIAS"] = (
        df_entrada["N COPIAS"]
        .fillna("0")                       # NaN → "0"
        .astype(str)
        .str.extract(r"^(\d+)")            # puede generar NaN
        .fillna("0")                       # limpia los NaN que deja extract
        .astype(int)
    )
    df_entrada = df_entrada.replace(r'^\s*$', pd.NA, regex=True)
    df_entrada["AGRUPACIÓN"] = df_entrada["AGRUPACIÓN"].fillna("")

    #Formatear solo si existen valores
    if not df_entrada["FECHA EJECUCIÓN"].isna().any():
        df_entrada["FECHA EJECUCIÓN"] = pd.to_datetime(df_entrada["FECHA EJECUCIÓN"].dt.strftime("%d-%m-%Y"), dayfirst=True).dt.normalize()

    if CopiarMuestras:
        df_entrada = df_entrada[df_entrada["N COPIAS"] != 0]

except ValueError as e:
    eprint(f"Error en formato de entrada al obtener numero de copias:\n{e}")
    input("Enter para cerrar...")
    exit(1)
    
dict_padre = {}

if len(set((df_entrada["AGRUPACIÓN"])))>1:

    inconsistencias = (df_entrada.groupby(["AGRUPACIÓN", "ID COTI"])["FECHA EJECUCIÓN"].nunique())
    errores = inconsistencias[inconsistencias > 1]

    if not errores.empty:
        detalles = [
            f"Agrupación '{agrup}' - Cotización {coti}"
            for agrup, coti in errores.index
        ]
        eprint(
            "Las siguientes cotizaciones tienen más de una fecha de ejecución "
            "dentro de su agrupación:\n"
            + "\n".join(detalles)
            + "\nUna cotización debe tener solo una fecha de ejecución por agrupación para el PE"
        )
        input("Enter para cerrar...")
        exit(1)

    eprint("Subiendo según columna agrupación")

    for (agrup, coti), grupo in df_entrada.groupby(
        ["AGRUPACIÓN", "ID COTI"], sort=False
    ):
        fecha = grupo["FECHA EJECUCIÓN"].iloc[0]

        if pd.isna(fecha):
            fecha_str = "None"
        else:
            fecha_str = pd.to_datetime(fecha).strftime("%d-%m-%Y")

        subclave = f"{coti}|{fecha_str}"

        dict_padre.setdefault(str(agrup), {})[subclave] = [
            str(x) for x in grupo["ID MUESTRA"]
        ]

else:

    inconsistencias = (
        df_entrada
        .groupby("ID COTI")["FECHA EJECUCIÓN"]
        .nunique()
    )

    cotis_con_error = inconsistencias[inconsistencias > 1]

    if not cotis_con_error.empty:
        eprint(
            f"Las siguientes cotizaciones tienen más de una fecha de ejecución: "
            f"{cotis_con_error.index.tolist()}\n"
            "Una cotización debe tener solo una fecha de ejecución para el PE"
        )
        input("Enter para cerrar...")
        exit(1)


    for coti, grupo in df_entrada.groupby("ID COTI", sort=False):
        fecha = grupo["FECHA EJECUCIÓN"].iloc[0]
        
        if pd.isna(fecha):
            fecha_str = "None"
        else:
            fecha_str = pd.to_datetime(fecha).strftime("%d-%m-%Y")

        clave = f"{coti}|{fecha_str}"

        dict_padre[clave] = [
            str(x) for x in grupo["ID MUESTRA"]
        ]

    dict_padre = {"": dict_padre}


try:

    prefs = prefs | {}
    DriverOptions.add_experimental_option("prefs",prefs)

    driver = Chrome(options=DriverOptions)
    eprint("Iniciando sesión en labsoft\n")

    Login(driver, path_internal=internal_lib, post_url=myLIMSdomain, login_url=Labsoftdomain)
    EsperarCARGA_myLIMS(driver, funcion_print=eprint, recargar=True)
    
    timer = DeltaTimer(buffer_size=10)
    timer.start(len(dict_padre.keys()))

    for key in dict_padre.keys():
        if key != "":
            eprint(f"División {key}")

        main_dict = dict_padre[key]

        lista_texto_coti = unique(main_dict.keys())
        lista_excluidos = [str(_) for _ in ListaMuestraXLSX(dirExcelSalida, colname=nombre_columnas_out[1], colnames=nombre_columnas_out) ]

        for coti in lista_excluidos:
            for texto_coti in lista_texto_coti:
                if coti in texto_coti:
                    if ExcluirExcelSalida:
                        eprint(f"Cotizacion {coti} ya en excel de salida, saltando...")
                        lista_texto_coti.remove(texto_coti)
                    else:
                        eprint(f"Cotizacion {coti} ya en excel de salida, repasando...")

        cantidad_cotizaciones = len(lista_texto_coti)

        eprint( f'\nCantidad de copias totales: {sum([int(_) for _ in list(df_entrada["N COPIAS"])])}\n'+
                f'Cotizaciones totales: {cantidad_cotizaciones}\n'+
                f'Cantidad de Muestras: {len(df_entrada["ID MUESTRA"])}\n'+
                f'Cotizaciones en ListaSalida: {len(lista_excluidos)}\n')

        eprint( f"Saltar muestras excel de salida: {ExcluirExcelSalida}\n"+
                f"Copiar muestras: {CopiarMuestras}\n"+
                f"Crear Preparacion Envase: {CrearPE}\n")

        if not cantidad_cotizaciones:
            eprint("SIN COTIZACIONES PARA PROCESAR")
            input("Enter para cerrar...")
            exit(0)

        if not CopiarMuestras and not CrearPE:
            eprint("Copiar y crear pe desactivado, nada que hacer...")
            input("Enter para cerrar...")
            exit(0)

        timer = DeltaTimer(buffer_size=10)
        timer.start(cantidad_cotizaciones)
        
        flag_alerta_inicial = True
        ##############################################

        for idx, texto_coti in enumerate(lista_texto_coti):
            slog()
            id_coti, fecha_ejecucion = texto_coti.split("|")

            #### EXCEL
            x_idx = idx
            x_id_coti = id_coti
            x_muestra_id = "###"
            x_copias_id = "###"
            x_pe_id = "###"
            x_pe_n_muestra = "###"
            x_pe_titulo = "###"
            x_xlsx_estado = "ERROR INICIO"
            x_xlsx_estado_final = []
            ####

            driver.get(f"{myLIMSdomain}Main.cshtml#Work/Details/{id_coti}") # error redirige a
            EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)
            
            if "Work/All/List" in driver.current_url:
                x_xlsx_estado = "COTI NO EXISTE"
                raise ExcepcionDeMuestra(f"[Cotizacion no existe]")

            if flag_alerta_inicial:
                flag_alerta_inicial = del_alertas_iniciales(driver, "//iframe[contains(@title,'Survey')]","//div[@role='button' and @aria-label='Close survey']")

            filtro = (
                (df_entrada["ID COTI"].astype(str) == str(id_coti)) &
                (df_entrada["AGRUPACIÓN"] == key)
            )

            if fecha_ejecucion != "None":
                filtro &= (
                    pd.to_datetime(df_entrada["FECHA EJECUCIÓN"], errors="coerce")
                    .dt.strftime("%d-%m-%Y")
                    ==
                    pd.to_datetime(fecha_ejecucion, dayfirst=True)
                    .strftime("%d-%m-%Y")
                )
            
            df_coti = df_entrada[filtro]

            lista_muestras_coti = main_dict[texto_coti]
            copias_totales = sum(list(df_coti["N COPIAS"]))

            timer.save(idx-1)

            eprint( f'Revisando Cotizacion: {id_coti} [{idx+1}/{cantidad_cotizaciones}]\n'+
                    f'Muestras de esta Cotizacion: {" ".join(lista_muestras_coti)}\n'+
                    f'{copias_totales} copias totales\n'
                    f'Tiempo restante: {timer.t_restante} [{timer.h_estimada}]\n')

            try:
                coti_activa = driver.find_element(By.XPATH, xpath_muestra_activa ).is_selected()
                coti_etapa = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='WorkFlowStepTo']/..//input[@class='k-input']").get_attribute("value")
                # coti_estado = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='SampleStatus']/..//input[@class='k-input']").get_attribute("value")
                coti_name_id = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='Identification' and @name='Identification']").get_attribute("value")

                if not copias_totales and CopiarMuestras:
                    x_xlsx_estado = "COTI DESACTIVADA"
                    raise ExcepcionDeMuestra(f"[Sin Copias en excel para cotizacion]")

                if not coti_activa:
                    x_xlsx_estado = "COTI DESACTIVADA"
                    raise ExcepcionDeMuestra(f"[Cotizacion desactivada]")

                if RevisarEtapaActual and coti_etapa != "En Realización":
                    x_xlsx_estado = f"COTI ETAPA {coti_etapa.upper()}"
                    raise ExcepcionDeMuestra(f"[Cotizacion en etapa {coti_etapa if coti_etapa else 'Vacío'}]")

                BotonSection(driver, "Muestras").click()
                EsperarCARGA_myLIMS(driver)

                control_grilla = driver.find_element(By.XPATH, "//div[contains(@class, 'k-pager-wrap') and contains(@class, 'k-widget') and @data-role='pager']")
                MuestrasCantidad = control_grilla.find_element(By.XPATH, ".//span[@class='k-pager-info k-label']").text

                if MuestrasCantidad == "Nada a enseñar.":
                    x_xlsx_estado = "COTI SIN MUESTRAS"
                    raise ExcepcionDeMuestra(f"Cotizacion {id_coti} no tiene muestras")

                else:
                    MuestrasCantidad = int(Cortar(MuestrasCantidad, "de ", " ítems"))

                m_copias_id = []
                m_no_copia = []
                m_copias = []

                if CopiarMuestras:
                    eprint(f"[Seleccionando ID para copiar]")

                    ############################################################################################
                    ## Seleccionar ID COPIA
                    if MuestrasCantidad <= 100:

                        tablaColnames = GetTablaColumna(driver, f"{xpath_seccion_muestras}/table/thead/tr")
                        elementos = driver.find_elements(By.XPATH, "//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[contains(@class, 'k-auto-scrollable')]/table/tbody/tr")
                        
                        ## Cargar Buffer m_copias
                        for muestra in elementos:
                            muestra_id = muestra.find_element(By.XPATH, f"./td[{tablaColnames['ID']}]").text
                            muestra_activa = (muestra.find_element(By.XPATH, f"./td[{tablaColnames['¿Activo?']}]").get_attribute("textContent") == "Si")

                            if muestra_id in lista_muestras_coti and muestra_activa:
                                muestra_idx = muestra.find_element(By.XPATH, f"./td[{tablaColnames['Orden']}]")

                                m_copias.append(muestra)
                                m_copias_id.append(muestra_id)

                        m_no_copia = unique(set(lista_muestras_coti) - set(m_copias_id))

                        #### EXCEL
                        if not m_no_copia: #No contiene errores
                            x_muestra_id = " - ".join(m_copias_id)
                        else:
                            eprint(f"[Muestras {' - '.join(m_no_copia)} no existen en cotizacion]")
                            x_muestra_id = f'{" - ".join(m_copias_id)} ![ {" - ".join(m_no_copia)} ]'
                            x_xlsx_estado_final.append("[COTI NO ENCUENTRA M]")
                        ####
                        
                        ## Seleccionar muestras para copiar
                        m_copia_1 = m_copias[0].find_element(By.XPATH, f"./td[{tablaColnames['Orden']}]")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", m_copia_1)
                        m_copia_1.click()

                        for _ in m_copias[1:]:
                            driver.execute_script("arguments[0].setAttribute('class', 'k-alt k-state-selected');", _)

                        driver.find_element(By.XPATH, f'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar"]//div[not(contains(@style, "display: none;"))]/button[@data-test="Copiar"]').click()
                        EsperarCARGA_myLIMS(driver)

                        ## Seleccionar cantidad en ventana
                        tablaColnames = GetTablaColumna(driver, f"{xpath_ventana_copia}//div[@class='k-grid-header']//thead/tr")
                        for v_elementos in driver.find_elements(By.XPATH, f"{xpath_ventana_copia}//tbody/tr"):
                            v_id = v_elementos.find_element(By.XPATH, f"./td[{tablaColnames['Id']}]").text
                            if v_id in lista_muestras_coti:
                                v_n_copias = int(list(df_coti[df_coti["ID MUESTRA"] == int(v_id)]["N COPIAS"])[0])

                                v_copia = v_elementos.find_element(By.XPATH, f"./td[{tablaColnames['N°de Copias']}]")
                                v_copia.click()
                                
                                v_copia = v_elementos.find_element(By.XPATH,f"./td[{tablaColnames['N°de Copias']}]//input[@class='k-input']")
                                v_copia.send_keys(Keys.CONTROL, "a")
                                v_copia.send_keys(Keys.DELETE)
                                v_copia.send_keys(v_n_copias)

                                v_copia.send_keys(Keys.ENTER)

                        else:
                            BotonVentana(driver,"Copiar").click()
                            EsperarCARGA_myLIMS(driver, reintentos=300)

                            xpath_estado_copia = f"{xpath_ventana_copia}//div[contains(text(),'Copias Concluidas.')]"
                            try:
                                WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, xpath_estado_copia)))
                            except Exception:
                                raise ExcepcionDeCarga(f"No apareció el mensaje 'Copias Concluidas.' dentro de la ventana: {xpath_estado_copia}")
                            
                            driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//button[@data-test="Cancelar" and contains(text(), "Salir")]').click()
                            EsperarCARGA_myLIMS(driver)

                    ############################################################################################
                    ## Seleccionar ID COPIA UNO POR UNO
                    else:
                        eprint(f"[Más de 100 muestras en grilla ({MuestrasCantidad}), haciendo busqueda por separado]")

                        for muestra in lista_muestras_coti:
                            
                            driver.find_element(By.XPATH, f"{xpath_sec_muestra}//th/span[@data-field='SampleId']//input[@type='text']").send_keys(muestra)
                            driver.find_element(By.XPATH,"//div[@class='mylimsweb-ui-main-header-interface-header-title']").click()
                            EsperarCARGA_myLIMS(driver)

                            try:
                                elemento_muestra = driver.find_element(By.XPATH, f"//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[contains(@class, 'k-auto-scrollable')]/table/tbody/tr[1]")
                                elemento_muestra.find_element(By.XPATH,"./td[1]").click()

                                m_copias_id.append(elemento_muestra.find_element(By.XPATH,"./td[2]").text)
                                
                                EsperarCARGA_myLIMS(driver)

                            except (NoSuchElementException,ElementNotInteractableException) as e:
                                m_no_copia.append(muestra)
                                
                                driver.find_element(By.XPATH, f"{xpath_sec_muestra}//th/span[@data-field='SampleId']//input[@type='text']").send_keys(Keys.CONTROL, "a", Keys.DELETE)
                                driver.find_element(By.XPATH,"//div[@class='mylimsweb-ui-main-header-interface-header-title']").click()
                                EsperarCARGA_myLIMS(driver)
                                
                                continue
                            
                            driver.find_element(By.XPATH, f'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar"]//div[not(contains(@style, "display: none;"))]/button[@data-test="Copiar"]').click()
                            EsperarCARGA_myLIMS(driver)

                            tablaColnames = GetTablaColumna(driver, f"{xpath_ventana_copia}//div[@class='k-grid-header']//thead/tr")
                            for v_elementos in driver.find_elements(By.XPATH, f"{xpath_ventana_copia}//tbody/tr"):
                                
                                v_id = v_elementos.find_element(By.XPATH, f"./td[{tablaColnames['Id']}]").text

                                if v_id in lista_muestras_coti:
                                    v_n_copias = int(list(df_coti[df_coti["ID MUESTRA"] == int(v_id)]["N COPIAS"])[0])

                                    v_copia = v_elementos.find_element(By.XPATH, f"./td[{tablaColnames['N°de Copias']}]")
                                    v_copia.click()

                                    v_copia = v_elementos.find_element(By.XPATH,f"./td[{tablaColnames['N°de Copias']}]//input[@class='k-input']")
                                    v_copia.send_keys(Keys.CONTROL, "a")
                                    v_copia.send_keys(Keys.DELETE)
                                    v_copia.send_keys(v_n_copias)

                                    v_copia.send_keys(Keys.ENTER)

                            else:
                                BotonVentana(driver,"Copiar").click()
                                EsperarCARGA_myLIMS(driver, reintentos=300)

                                xpath_estado_copia = f"{xpath_ventana_copia}//div[contains(text(),'Copias Concluidas.')]"
                                try:
                                    WebDriverWait(driver, 360).until(EC.presence_of_element_located((By.XPATH, xpath_estado_copia)))
                                except Exception:
                                    raise ExcepcionDeCarga(f"No apareció el mensaje 'Copias Concluidas.' dentro de la ventana: {xpath_estado_copia}")
                                
                                driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//button[@data-test="Cancelar" and contains(text(), "Salir")]').click()
                                EsperarCARGA_myLIMS(driver)

                                driver.find_element(By.XPATH, f"{xpath_sec_muestra}//th/span[@data-field='SampleId']//input[@type='text']").send_keys(Keys.CONTROL, "a", Keys.DELETE)
                                driver.find_element(By.XPATH,"//div[@class='mylimsweb-ui-main-header-interface-header-title']").click()
                                EsperarCARGA_myLIMS(driver)

                            logprint(f"muestra {muestra} lista con {v_n_copias} copias")

                        #### EXCEL
                        if not m_no_copia: #No contiene errores
                            x_muestra_id = " - ".join(m_copias_id)
                        else:
                            eprint(f"[Muestras {' - '.join(m_no_copia)} no existen en cotizacion]")
                            x_muestra_id = f'{" - ".join(m_copias_id)} ![ {" - ".join(m_no_copia)} ]'
                            x_xlsx_estado_final.append("[COTI NO ENCUENTRA M]")
                        ####

                    ###################
                    ## Obtener nueva cantidad de copias
                    control_grilla = driver.find_element(By.XPATH, "//div[contains(@class, 'k-pager-wrap') and contains(@class, 'k-widget') and @data-role='pager']")
                    MuestrasCantidadNueva = control_grilla.find_element(By.XPATH, ".//span[@class='k-pager-info k-label']").text

                    if MuestrasCantidadNueva == "Nada a enseñar.":
                        x_xlsx_estado = "COTI SIN MUESTRAS"
                        raise ExcepcionDeMuestra(f"Cotizacion {id_coti} no tiene muestras")

                    else:
                        MuestrasCantidadNueva = int(Cortar(MuestrasCantidadNueva, "de ", " ítems"))

                    flag_DiferenciaCantidad = (MuestrasCantidadNueva != MuestrasCantidad+int(copias_totales))

                    if flag_DiferenciaCantidad:
                        eprint(f"[Cantidad de muestras copiadas no coincide con copias programadas]")
                        logprint(f"DIFERENCIAS DE CANTIDAD {MuestrasCantidad} muestras + {copias_totales} copias != {MuestrasCantidadNueva} nuevas cantidad de muestras totales")
                    
                    copias_reales = MuestrasCantidadNueva - MuestrasCantidad
                    
                    if copias_reales > 100:
                        eprint(f"[MÁS DE 100 COPIAS, asignando de primeras 100 a PE ({copias_reales} restantes)]")
                        cant_copias = 100
                    else:
                        cant_copias = copias_reales

                else:
                    eprint(f"[Saltando copia ID]")
                    cant_copias = 0
                    copias_reales = 0

                    x_copias_id = "SIN COPIAS"

                m_selec_id = []
                m_no_selec = []
                m_selec = []

                tablaColnames = GetTablaColumna(driver, f"{xpath_seccion_muestras}/table/thead/tr")
                elementos = driver.find_elements(By.XPATH, f"{xpath_seccion_muestras}/table/tbody/tr")
                
                #CLIENTE DE ULTIMA MUESTRA CREADA
                m_cliente = elementos[1].find_element(By.XPATH,f"./td[{tablaColnames['Cuenta']}]").text
                if not SufijoTituloGeneral:
                    pe_titulo = f"PE - {m_cliente} - {coti_name_id}"
                else:
                    pe_titulo = f"PE - {m_cliente} - {coti_name_id} - {SufijoTituloGeneral}"

                logprint(f"titulo: {pe_titulo}")
                x_pe_titulo = pe_titulo

                ############################################################################################
                ## Seleccionar Nuevas Muestras para CREAR ENVASE
                if CrearPE:
                    ## Invertir Orden
                    driver.find_element(By.XPATH,"//div[@id='InterfaceContent']/div[not(contains(@style, 'display: block;'))]//th[@data-title='Orden']").click()
                    EsperarCARGA_myLIMS(driver)
                    
                    eprint(f"[Seleccionando ID para PE]")

                    #Crear pe de muestras nuevas copiadas
                    if CopiarMuestras:

                        for idx in range(cant_copias):
                            tablaColnames = GetTablaColumna(driver, f"{xpath_seccion_muestras}/table/thead/tr")
                            elementos = driver.find_elements(By.XPATH, f"{xpath_seccion_muestras}/table/tbody/tr")
                            muestra = elementos[idx]

                            muestra_id = muestra.find_element(By.XPATH, f"./td[{tablaColnames['ID']}]").text
                            muestra_activa = (muestra.find_element(By.XPATH, f"./td[{tablaColnames['¿Activo?']}]").get_attribute("textContent") == "Si")

                            if not muestra_activa:
                                continue

                            m_selec.append(muestra)
                            m_selec_id.append(muestra_id)

                        if m_selec_id:
                            x_copias_id = " - ".join(m_selec_id)
                            ultimo_id = m_selec_id[-1]
                            eprint(f"[Úlitmo ID seleccionado: {ultimo_id}]")

                            if cant_copias >100:
                                eprint(f"[Más de 100 copias, faltan {cant_copias-100}]")
                                x_xlsx_estado_final.append(f"[M100C ({cant_copias-100}) ({ultimo_id})]")
                        else:
                            eprint(f"[No se encontraron las copias]")

                    if not CopiarMuestras: # x_muestra con selec y x_copia con ### 
                        x_copias_id = "###"
                        
                        ## Cargar Buffer m_selec
                        for muestra in elementos:
                            muestra_id = muestra.find_element(By.XPATH, f"./td[{tablaColnames['ID']}]").text
                            muestra_activa = (muestra.find_element(By.XPATH, f"./td[{tablaColnames['¿Activo?']}]").get_attribute("textContent") == "Si")

                            if muestra_id in lista_muestras_coti and muestra_activa:
                                muestra_idx = muestra.find_element(By.XPATH, f"./td[{tablaColnames['Orden']}]")

                                m_selec.append(muestra)
                                m_selec_id.append(muestra_id)

                        m_no_selec = unique(set(lista_muestras_coti) - set(m_selec_id))

                        #### EXCEL
                        # usar x_muestra_id como muestras a seleccionar
                        if m_no_selec: 
                            if len(lista_muestras_coti) >100:
                                eprint(f"[Más de 100 muestras para asociar a envase {' - '.join(m_no_selec)} no fueron seleccionadas]")
                                x_muestra_id = f'{" - ".join(m_selec_id)} ![ {" - ".join(m_no_selec)} ]'
                                x_xlsx_estado_final.append("[M100M]")        
                            else:
                                eprint(f"[Muestras {' - '.join(m_no_selec)} no existen en cotizacion]")
                                x_muestra_id = f'{" - ".join(m_selec_id)} ![ {" - ".join(m_no_selec)} ]'
                                x_xlsx_estado_final.append("[COTI NO ENCUENTRA M PE]")
                            
                        else:  #No contiene errores
                            x_muestra_id = " - ".join(m_selec_id)
                        ####
                    
                    if m_selec_id:
                        ultimo_id = m_selec_id[-1] if m_selec_id else "None"
                        
                        ## Seleccionar muestras para copiar
                        
                        m_selec_1 = m_selec[0].find_element(By.XPATH, f"./td[{tablaColnames['Orden']}]")
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", m_selec_1)
                        m_selec_1.click()

                        for _ in m_selec[1:]:
                            driver.execute_script("arguments[0].setAttribute('class', 'k-alt k-state-selected');", _)

                        botones_accion = driver.find_element(By.XPATH, "//div[@id='InterfaceActions']//div[@class='labsoft-ui-buttons-bar']")
                        driver.execute_script("""
                            arguments[0].setAttribute('tabindex', '-1');
                            arguments[0].focus();
                        """, botones_accion)

                        [botones_accion.send_keys(Keys.ARROW_RIGHT) for _ in range(4)]
                        eprint(f"[Creando PE]")

                        boton_actividad = BotonAccion(driver,"Actividades")
                        boton_actividad.click()
                        EsperarCARGA_myLIMS(driver)

                        x_xlsx_estado = "ERROR ACTIVIDADES"

                        boton_actividad.find_element(By.XPATH, "./../ul/li[@data-test='Crear']").click()
                        EsperarCARGA_myLIMS(driver)
                        
                        driver.find_element(By.XPATH, "//div[contains(@class, 'k-window')]//td[contains(text(),'Preparación de Envases')]").click()
                        EsperarCARGA_myLIMS(driver)

                        BotonVentana(driver,"Seleccionar").click()
                        EsperarCARGA_myLIMS(driver)

                        nuevas_ventanas = driver.find_elements(By.XPATH, "//body/div[contains(@class, 'k-window') and contains(@style, 'display: block;')]")

                        if len(nuevas_ventanas) != 1:
                            x_xlsx_estado = "ALERTA INESPERADA"
                            str_salida = ""

                            logprint("lista alertas: ")

                            for _ in nuevas_ventanas:
                                titulo = _.find_element(By.XPATH,".//span[@class='k-window-title']").text
                                cuerpo = _.find_element(By.XPATH,".//div[contains(@class, 'k-window-content')]").text
                                str_salida = str_salida+f"\n- {titulo}"
                                logprint(f"t: {titulo}\nc: {cuerpo}\n")

                            raise ExcepcionDeMuestra(f"Alertas Inesperadas (más info en el log), titulos encontrados de ventanas: {str_salida}")
                        
                        EsperarCARGA_myLIMS(driver)

                        responsable = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='ResponsibleUser']/..//input[@class='k-input']").get_attribute("value")
                        if not responsable:
                            #### EXCEL
                            x_pe_id = "###"
                            x_pe_n_muestra = "###"
                            ####
                            
                            x_xlsx_estado_final.append("[ERROR MYLIMS]")    
                            raise ExcepcionDeMuestra(f"Carga de PE interrumpida, mylims no carga datos")

                        if paisActual == "colombia":
                            driver.find_element(By.XPATH, "//div[contains(@class, 'k-window')]//td[contains(text(),'Peso Colombiano')]").click()
                            logprint("click en peso colombiano")

                        elif paisActual == "mexico":
                            driver.find_element(By.XPATH, "//div[contains(@class, 'k-window')]//td[contains(text(),'Peso Mexicano')]").click()
                            logprint("click en peso mexicano")

                        else:
                            driver.find_element(By.XPATH, "//div[contains(@class, 'k-window')]//td[contains(text(),'Unidad de Fomento')]").click()
                            logprint("click en unidad de fomento")

                        BotonVentana(driver,"Confirmar").click()
                        EsperarCARGA_myLIMS(driver)

                        pe_identification = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='Identification' and @name='Identification']")
                        pe_identification.send_keys(pe_titulo)

                        if fecha_ejecucion != "None":
                            pe_fecha_ejecucion = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='Execution' and @name='Execution']")
                            pe_fecha_ejecucion.click()
                            
                            pe_fecha_ejecucion.send_keys(Keys.CONTROL, "a")
                            pe_fecha_ejecucion.send_keys(Keys.DELETE)
                            input(f"Fecha de ejecución: {fecha_ejecucion}")
                            pe_fecha_ejecucion.send_keys(fecha_ejecucion)
                            

                        BotonAccion(driver,"SaveButton").click()
                        EsperarCARGA_myLIMS(driver)
                        
                        #### EXCEL
                        x_pe_id = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='Id' and @name='Id']").get_attribute("value").replace("\'", "")
                        x_pe_n_muestra = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']//input[@data-test='ControlNumber' and @name='ControlNumber']").get_attribute("value")
                        ####

                        eprint(f"[PE creado ({x_pe_id}) - ({x_pe_n_muestra}) - ({x_pe_titulo})]\n")
                    else:

                        #### EXCEL
                        x_pe_id = "###"
                        x_pe_n_muestra = "###"
                        ####
                        
                        x_xlsx_estado_final.append("[SIN MUESTRAS SELEC]")    
                        eprint(f"[No se han seleccionado muestras]")

                else:

                    #### EXCEL
                    x_pe_id = "SIN PE"
                    x_pe_n_muestra = "SIN PE"
                    ####
                    
                    #Obtener lista de copia
                    tablaColnames = GetTablaColumna(driver, f"{xpath_seccion_muestras}/table/thead/tr")
                    elementos = driver.find_elements(By.XPATH, f"{xpath_seccion_muestras}/table/tbody/tr")
                    for idx in range(copias_reales):
                        muestra = elementos[idx]
                        muestra_id = muestra.find_element(By.XPATH, f"./td[{tablaColnames['ID']}]").text
                        muestra_activa = (muestra.find_element(By.XPATH, f"./td[{tablaColnames['¿Activo?']}]").get_attribute("textContent") == "Si")
                        
                        if not muestra_activa:
                            continue

                        m_selec_id.append(muestra_id)

                    x_copias_id = " - ".join(m_selec_id)
                    
                    eprint(f"[Saltando creación de PE]\n")
                
                x_xlsx_estado = "LISTO" if not x_xlsx_estado_final else " - ".join(x_xlsx_estado_final)
                FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=[x_idx, x_id_coti, x_muestra_id, x_copias_id, x_pe_id, x_pe_n_muestra, x_pe_titulo, x_xlsx_estado], colnames=nombre_columnas_out, except_kill=False, except_create=True)

                if CopiarMuestras and CrearPE:
                    logprint(f"coti {id_coti} y sus muestras {lista_muestras_coti} con las siguientes muestras copiadas: {m_selec_id}")

                if not CopiarMuestras and CrearPE:
                    logprint(f"pe creado para muestras {m_selec_id} en la coti {id_coti}")

                if CopiarMuestras and not CrearPE:
                    logprint(f"coti {id_coti} y sus muestras {lista_muestras_coti} con las siguientes muestras copiadas: {m_selec_id}")

            except Exception as e:
                Excepcion_error = e
                
                cantidad_ventanas = 0
                driver.execute_script("window.onbeforeunload = null;")

                #Conexion a internet
                while True:
                    try:
                        requests.head("http://www.google.com/", timeout=5)
                        break
                    except requests.ConnectionError:
                        eprint("No hay connexión a internet, reintentando cada 1 minuto...")
                        sleep(60)

                #Contar ventanas
                try:
                    mylims_ventanas = driver.find_elements(By.XPATH, "//body/div[contains(@class, 'k-window') and contains(@style, 'display: block;')]")
                    titulos = " - ".join([_.find_element(By.XPATH,".//span[@class='k-window-title']").text for _ in mylims_ventanas])
                    cuerpos = " - ".join([_.find_element(By.XPATH,".//div[contains(@class, 'k-window-content')]").text for _ in mylims_ventanas])
                    cantidad_ventanas = len(mylims_ventanas)

                except NoSuchElementException:
                    titulos = "ERROR"
                    cantidad_ventanas = "ERROR"

                if isinstance(e, (ExcepcionDeMuestra,UnexpectedAlertPresentException, StaleElementReferenceException) ):
                    eprint(f'__________________\nProblemas con la cotizacion {id_coti}\n{FormatoExcepcion(e)}\n')

                if isinstance(e, (InvalidSessionIdException, ExcepcionDeCarga) ):
                    eprint(f'__________________\nProblemas con la Navegador en la cotizacion {id_coti}\n{FormatoExcepcion(e)}\n')

                if isinstance(e, KeyError):
                    eprint(f'__________________\nProblemas Internos en el proceso\n{FormatoExcepcion(e)}\n')

                #ELSE
                if not isinstance(e, (ExcepcionDeMuestra, UnexpectedAlertPresentException, StaleElementReferenceException, InvalidSessionIdException, ExcepcionDeCarga, KeyError) ):
                    eprint(f'__________________\nProblemas desconocidos con la cotizacion {id_coti}\n{FormatoExcepcion(e)}\n')

                #Anunciar ventanas
                if cantidad_ventanas != 0:
                    logprint(f'__________________\nCantidad de ventanas: {cantidad_ventanas} \nTitulos: {titulos} \nCuerpos: {cuerpos} \n{FormatoExcepcion(e)}\n') 
                    
                sleep(1)
                FilaAgregarXLSX(dirExcel=dirExcelSalida, valores_fila=[x_idx, x_id_coti, x_muestra_id, x_copias_id, x_pe_id, x_pe_n_muestra, x_pe_titulo, x_xlsx_estado], colnames=nombre_columnas_out, except_kill=False, except_create=True)

                driver.get(myLIMSdomain)
                EsperarCARGA_myLIMS(driver, funcion_print=eprint)
                continue

            except BaseException as e:
                eprint(f"Error para la cotizacion {id_coti}:\n\n {FormatoExcepcion(e)}")
                notify(title=f"Problemas con la cotizacion {id_coti}!", body=type(e).__name__)
                sleep(3)
                break

    else:
        eprint(f"Programa finalizado... Cerrando\n")
        notify(title="Programa finalizado")
        Logout(driver,logout_url=Labsoftdomain)
        driver.quit()

    ##############################################

except NoSuchWindowException:
    eprint("Ventana de navegador cerrada")

except KeyboardInterrupt:
    eprint("Programa interrumpido...\n Cerrando navegador")
    try:
        Logout(driver,logout_url=Labsoftdomain)
        driver.quit()
    except NameError:
        pass