#ACTUALIZAR CHROMIUN CON https://download-chromium.appspot.com/
try:
    
    import sys,os
    from datetime import datetime

    file_name           =   os.path.basename(__file__)
    DM_wd               =   os.path.dirname(os.path.realpath(__file__))
    internal_lib        =   os.path.normpath(os.path.join(DM_wd,"..","internal_lib"))

    sys.path.insert(0, internal_lib)

    from __myLIMS_modulos__ import (
        GetConfig, MensajeInicial, version_actual, existe_param_env,
        EsperarCARGA_myLIMS, ExcepcionDeCarga, ChequearNavegador,
        BotonSection, BotonAccion, BotonVentana, queue_redy, internet_ok,
        ElementClickInterceptedException, ExcepcionArchivo,
        FormatoExcepcion, ExcepcionDeMuestra, ElementNotInteractableException,
        UnexpectedAlertPresentException, StaleElementReferenceException, InvalidSessionIdException, 
        By, EC, DriverOptions, Chrome, Keys, WebDriverWait, DeltaTimer, alerta_visible,
        notify, sleep, datetime, requests, prefs, Path, EsperarCLICK, get
    )
    from __myLIMS_wrappers__ import (
        unique, Cortar, BuscarAlertas,
        ContarControlesPendientes,
        CambiarFechas, MuestraPublicar,
        DesactivarAlerta, CambiarAcreditacion
    )
    from __ficheros_modulos__ import (
        ListaMuestraXLSX, FilaAgregarXLSX,
        ObtenerIDExcel, AgregarMuestraXLSX,
    )
    from __myLIMS_wrappers__ import (
        Logout, Login, FormatoLimiteHoras,
    )
    from __myLIMS_API__ import (
        get_samples_ID,
    )

    ########################################
    #Inicialización de Config
    ########################################
    try:
        config              =   GetConfig( dirConfig=os.path.join(DM_wd,"config.txt") )
        global_config       =   GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )

        keys_used   = ["filtro", "SoloBuscarControles", "DescargarPublicadas", "RegistrarMuestras", "RevisarRutinas", "AutoPublicar", "Olvidar", "BorrarDuplicados", "Alerta", "DOC_REVISION_ETFA_ID_CL", "DOC_REVISION_ID_CL", "nombreExcelRegistro", "nombreExcelHistorico"]
        keys_used_g = ["myLIMSdomain", "Labsoftdomain", "paisActual", "ActivarLOG", "InicioJornada", "ExtensionJornada", "ListaMensajesRutina", "ListaMensajesHoras", "nombreExcelExcepciones", "TipoMensajeETFA", "api-url"]

        for key in keys_used:
            if key not in config.keys():
                input(f"Valor de config \'{key}\' no encontrado en archivo config, enter para continuar igualmente...")
        for key in keys_used_g:
            if key not in global_config.keys():
                input(f"Valor de config \'{key}\' no encontrado en archivo global_config, enter para continuar igualmente...")

        timeout             =   120
        timeout_con_check   =   3

        nombreLOG     = os.path.join(DM_wd, "log", datetime.now().strftime('reporte_%Y_%m_%d-%H_%M'))
        nombreRESUMEN = f"{nombreLOG}_RESUMEN.txt"

        myLIMSdomain  = global_config.get("myLIMSdomain", "")
        Labsoftdomain = global_config.get("Labsoftdomain", "")
        api_url       = global_config.get("api-url", "")

        paisActual = global_config.get("paisActual", "").replace("é","e").replace("ú","u").lower()
        log        = global_config.get("ActivarLOG", True)

        INICIO_JORNADA    = global_config.get("InicioJornada", "")
        EXTENSION_JORNADA = global_config.get("ExtensionJornada", "")

        tipo_rutinas = global_config.get("ListaMensajesRutina", "")
        tipo_rutinas = tipo_rutinas.lower().split(",") if tipo_rutinas else []

        tipo_horas = global_config.get("ListaMensajesHoras", "")
        tipo_horas = tipo_horas.lower().split(",") if tipo_horas else []

        TipoMensajeETFA = global_config.get("TipoMensajeETFA").lower()

        filtroActual = config.get("filtro", "").replace("é","e").replace("ú","u").lower()

        SoloBuscarControles = config.get("SoloBuscarControles", True)
        DescargarPublicadas = config.get("DescargarPublicadas", False)
        
        Alerta          = config.get("Alerta", True)
        AutoPublicar    = config.get("AutoPublicar", True)

        CorregirETFA    = config.get("CorregirETFA", True)
        RevisarRutinas  = config.get("RevisarRutinas", True)
        Olvidar         = config.get("Olvidar", False)
        Registrar       = config.get("RegistrarMuestras", True)
        TotalReintentos = config.get("TotalReintentos", 5)

        BorrarDup = config.get("BorrarDuplicados", True)

        id_etfa_config    = str(config.get("DOC_REVISION_ETFA_ID_CL", "")).split(",") if config.get("DOC_REVISION_ETFA_ID_CL") else []
        id_no_etfa_config = str(config.get("DOC_REVISION_ID_CL", "")).split(",") if config.get("DOC_REVISION_ID_CL") else []

        nombreExcelRegistro = config.get("nombreExcelRegistro", "Registro.xlsx")
        dirExcelRegistro    = os.path.join(DM_wd, nombreExcelRegistro) if nombreExcelRegistro else ""

        nombreHistorico   = config.get("nombreExcelHistorico", "Historico.xlsx")
        dirExcelHistorico = os.path.join(DM_wd, nombreHistorico) if nombreHistorico else ""
        nombreExcepciones = global_config.get("nombreExcelExcepciones", "Excepciones.xlsx")
        dirExcepciones    = os.path.join(internal_lib, nombreExcepciones)
	
        mainUrl                 =   f"{myLIMSdomain}Main.cshtml#Sample/Finalized/List"
        nombre_columnas         =   ["ID MUESTRAS"]
        nombre_columnas_reg     =   ["ID", "ID MUESTRAS", "TIENE CONTROLES", "TIENE RUTINAS", "TIENE ETFA", "MARCA"]

        if log:
            print("Historial de log activo\n")
            
            if not os.path.isdir( os.path.join(DM_wd,"log") ): os.mkdir(os.path.join(DM_wd,"log"))

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

        limite_inferior, limite_superior = FormatoLimiteHoras(INICIO_JORNADA, EXTENSION_JORNADA)

        if SoloBuscarControles:
            eprint(
                f"Solo Buscar Controles y alertas [True]:\t{SoloBuscarControles}\n\n"+
                f"Publicación automática [True]:\t{AutoPublicar}\n\n"+
                f"Olvidar registro [False]:\t{Olvidar}\n\n"+
                f"Revisar Rutinas [True]:\t\t{RevisarRutinas}\n\n"+
                f"País:\t\t\t\t{paisActual}\n\n"+
                f"Filtro Actual:\t\t\t{filtroActual}\n\n"+
                f"Rango Horario Laboral:\t\t{limite_inferior.strftime('%H:%M')} - {limite_superior.strftime('%H:%M')}\n"
                )
        else:

            dir_Descargados     =   os.path.join(DM_wd, "Descargados")
            
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

            eprint( f"Publicación automática [True]:\t{AutoPublicar}\n\n"+
                    f"Olvidar registro [False]:\t{Olvidar}\n\n"+
                    f"Registrar descargado [True]:\t{Registrar}\n\n"+
                    f"Revisar Rutinas [True]:\t\t{RevisarRutinas}\n\n"+
                    f"País:\t\t\t\t{paisActual}\n\n"+
                    f"Filtro Actual:\t\t\t{filtroActual}\n\n"+
                    f"Rango Horario Laboral:\t\t{limite_inferior.strftime('%H:%M')} - {limite_superior.strftime('%H:%M')}\n"
            )
            
            prefs = prefs | {
                'download.default_directory' : dir_Descargados,
                "savefile.default_directory": dir_Descargados,
            }

        ID_Excepciones = unique(ListaMuestraXLSX(dirExcel=dirExcepciones, colname=nombre_columnas[0], colnames=nombre_columnas))
        ID_Historico   = unique(ListaMuestraXLSX(dirExcel=dirExcelHistorico, colname=nombre_columnas[0], colnames=nombre_columnas))
        ID_Registrados = unique(ListaMuestraXLSX(dirExcel=dirExcelRegistro, colname=nombre_columnas_reg[1], colnames=nombre_columnas_reg))

        str_alerta = []
        
        if AutoPublicar and not RevisarRutinas:
            str_alerta.append("Publicacion sin revisar alertas de rutina")

        if not SoloBuscarControles or not AutoPublicar or Olvidar or not Registrar:
            str_alerta.append("Configuración ha sido alterada")
        
        if str_alerta:
            if Alerta:
                input(f"{", ".join(str_alerta)}, presione enter para continuar\n")
            else:
                print(f"{", ".join(str_alerta)}\n")

        if not Olvidar:
            ID_Excluidos = unique(ID_Excepciones + ID_Registrados + ID_Historico)
        else:
            ID_Excluidos = unique(ID_Excepciones)
        
        eprint(f"ID de muestras Registradas: {len(ID_Registrados)}\n"+
               f"ID de muestras Historicas: {len(ID_Historico)}\n"+
               f"ID de muestras Excepciones: {len(ID_Excepciones)}\n"+
               f"ID totales: {len(ID_Excluidos)}\n")

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
                                            "1193"],   #Aguas

                    "mexico"            :   ["1124"],   #Análisis    
                }[paisActual]

            for id in id_etfa_config+id_no_etfa_config:
                if id not in IDbotonesDocumentos: IDbotonesDocumentos.append( str(id) )

        except KeyError as e:
            eprint(f"El valor del filtro: {filtroActual} no fue reconocido por el programa (config.txt)\n{e}\n")
            input("Enter para cerrar...")
            exit(1)

        prefs = prefs | {}
        DriverOptions.add_experimental_option("prefs",prefs)
                
        F_Inicial = datetime.now().strftime('%d-%m %H:%M')
        
        if not existe_param_env(internal_lib):
            eprint("Error No se encontró archivo con credenciales. (Param.env)")
            input("Enter para cerrar..")
            exit(1)

        driver = Chrome(options=DriverOptions)
        eprint("Iniciando sesión en labsoft\n")

        try:
            Login(driver, path_internal=internal_lib, post_url=mainUrl, login_url=Labsoftdomain)

        except ExcepcionDeCarga as e:
            eprint(f"{e}\n")
            input("Enter para cerrar...")
            exit(1)
        eprint("Obteniendo listado de muestras")

        ListaMuestras = get_samples_ID(
            "Account ne null and Active eq true and endswith(ControlNumber, '.0') and "+
            "CurrentStatus/SampleStatus/Identification eq 'Finalizada' and "+
            "ServiceCenter/Identification eq 'Hidrolab SCL'",
            APIdomain=api_url,
            funcion_print=eprint, 
            funcion_logprint = logprint,
        )

    except Exception as e:
        notify(title="Problemas en programa", body=type(e).__name__)
        eprint(f"{FormatoExcepcion(e)}\nError al cargar myLIMS")
        input("Enter para cerrar navegador")
        Logout(driver,logout_url=Labsoftdomain)
        driver.quit()
        exit(1)

    Borrados = len(list(set(ListaMuestras) & set(ID_Excluidos)))
    ListaMuestras = [_ for _ in ListaMuestras if _ not in ID_Excluidos]

    MuestrasCantidad = len(ListaMuestras)
    MuestrasError = []

    TotalDescarga = 0
    TotalPublicados = 0
    
    N_Muestra = 0
    MuestraIndice = 1
    ID_Actual = 0

    if RevisarRutinas: 
        TotalCambioFechas = 0
        TotalDesacreditar = 0

    if SoloBuscarControles:
        eprint(f'Se agregaron {MuestrasCantidad} muestras a la cola y excluyeron {Borrados}, revisando controles y fechas para publicar...')
    else:
        eprint(f'Se agregaron {MuestrasCantidad} muestras a la cola y excluyeron {Borrados}, descargando...')

    id_excel = ObtenerIDExcel(dirExcel=dirExcelRegistro, ncol=0, colnames=nombre_columnas_reg)

    id_excel += 1
    fila_muestra = [ id_excel, "##########", "##########", "##########", "##########", datetime.now().strftime('[%d-%m-%Y %H:%M]')]
    FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    

    timer = DeltaTimer(buffer_size=25)
    timer.start(len(ListaMuestras))

    ########################################
    #Instancia para cada muestra a descargar
    for MuestraIndice, ID_Actual in enumerate(ListaMuestras,1):
        EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)

        slog()

        id_excel += 1

        timer.save(MuestraIndice)

        Excepcion_error = ""
        IntentosDeCarga = TotalReintentos

        if not SoloBuscarControles:
            cant_previa = len(os.listdir(dir_Descargados))
        else:
            cant_previa = 0

        while IntentosDeCarga != 0:
            #Reintentar y recargar solo esta sección
            try:
                flagDescargar = False
                flagCambiarFecha = False
                flagRutina = False
                flagDesacreditar = False
                flagControles = False

                checkCambiarFechas = False
                checkDesacreditar = False
                
                ChequearNavegador(driver, kill=True)

                driver.get(f"{myLIMSdomain}Main.cshtml#Sample/Details/{ID_Actual}")
                EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)

                N_Muestra = driver.find_element(By.XPATH, '//input[@data-test="ControlNumber"]').get_attribute("value")
                cliente = driver.find_element(By.XPATH, '//input[@data-bind="value: Account.Identification"]').get_attribute("value")
                
                texto_por_muestra = f"""
Revisando ID: {ID_Actual}
N de Muestra: {N_Muestra}
Tiempo restante: {timer.t_restante} [{timer.h_estimada}]
Muestras Restantes: {MuestrasCantidad-MuestraIndice} Muestras [{MuestraIndice}/{MuestrasCantidad}]
"""                
                texto_por_muestra = f"{texto_por_muestra}Registradas: {TotalDescarga} - " if SoloBuscarControles else f"{texto_por_muestra}Descargadas: {TotalDescarga} - "
                texto_por_muestra = f"{texto_por_muestra}Publicadas: {TotalPublicados}" if AutoPublicar else f"{texto_por_muestra}Publicables: {TotalPublicados}"
                texto_por_muestra = f"{texto_por_muestra}\nCambios de Acreditación: {TotalDesacreditar} - " if CorregirETFA else f"{texto_por_muestra}\nProblemas ETFA: {TotalDesacreditar} - "
                texto_por_muestra = f"{texto_por_muestra}Cambios de Fechas: {TotalCambioFechas}" if RevisarRutinas else ""

                eprint(texto_por_muestra)
                
                muestra_estado = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']/div[1]/div[1]//div[5]/div[3]//input[@class='k-input']").get_attribute("value")
                
                # muestra_fmuestreo   = driver.find_element(By.XPATH, "//input[@data-test='TakenDateTime']").get_attribute("value").replace("-", "/")
                # muestra_frecepcion  = ":".join(fila.find_element(By.XPATH, './td[@data-test="StatusHistoryGrid.EditionDateTime"]').text.replace("-", "/").split(":")[:-1])
                
                if muestra_estado == "Publicada":
                    eprint("[Previamente Publicada]\n")

                    if not DescargarPublicadas: 
                        fila_muestra = [ id_excel, ID_Actual, "YA PUBLICADA", "YA PUBLICADA", "YA PUBLICADA", ""]
                        FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                        AgregarMuestraXLSX(dirExcel=dirExcelHistorico, ID_Muestra=ID_Actual, colnames=nombre_columnas)
                        break
                    else:
                        flagDescargar = True
                        
                BotonSection(driver,"SectionMessage").click()
                EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)

                ###################################################
                #Revisar mensajes
                flagCambiarFecha, flagRutina, flagDesacreditar = BuscarAlertas(driver, tipo_rutinas, tipo_horas, TipoMensajeETFA, funcion_print=eprint)
                EsperarCARGA_myLIMS(driver)
                
                ###################################################
                #Hacer Cambios
                if (flagCambiarFecha or flagDesacreditar) and not flagDescargar:
                    
                    checkCambiarFechas = flagCambiarFecha
                    checkDesacreditar = flagDesacreditar

                    if RevisarRutinas: 

                        elemento_filtro = driver.find_element(By.XPATH, "//input[@class='select2-search__field' and @placeholder='Filtro del mensaje']")
                        elemento_filtro.click()
                        elemento_filtro.send_keys("tipo:horas")
                        elemento_filtro.send_keys(Keys.ENTER)

                        BotonAccion(driver,"Filtro").click()
                        EsperarCARGA_myLIMS(driver)

                        xpath_mensajes = '//div[@class="myLIMSweb-mail-list-item-box"]//li[contains(@class, "list-group-item")]'
                        
                        # Lista de li
                        lista_alertas = driver.find_elements(By.XPATH, xpath_mensajes) 
                        
                        # Asignar índice de li
                        lista_alertas = sorted([f"({xpath_mensajes})[{i+1}]" for i in range(len(lista_alertas))], reverse=True)

                        #Lista de alertas para desactivar
                        lista_alertas_pop = []

                        for m_index, iter_xpath in enumerate(lista_alertas):
                            lista_cambios = []
                            
                            mensaje     = driver.find_element(By.XPATH, iter_xpath)

                            m_tipo      = mensaje.find_element(By.XPATH,'./div/div[3]').text.lower()
                            m_inicio    = mensaje.find_element(By.XPATH,'./div/div[2]/div[1]').text
                            m_state     = mensaje.get_attribute("class")

                            if "inactive" in m_state:
                                lista_alertas_pop.append(m_index)
                                continue  

                            if m_tipo in tipo_horas:
                                eprint(f"[\"{m_inicio}\"]")
                                
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
                                        DesactivarAlerta(driver, iter_xpath, funcion_print=eprint)
                                        eprint("[Procesada Alerta de Horas]")

                                    else:
                                        eprint("[Problemas con las Horas]")
                                        checkCambiarFechas = False

                                except (ElementClickInterceptedException,ElementNotInteractableException) as e:
                                    raise ExcepcionDeMuestra("Error al cambiar fechas (Reintentar)")
                        
                            if m_tipo == TipoMensajeETFA:

                                eprint(f"[\"{m_inicio}\"]")

                                if not CorregirETFA:
                                    flagDescargar = True
                                    
                                else:
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
                                        if CambiarAcreditacion(driver, lista_cambios, funcion_print=logprint):
                                            DesactivarAlerta(driver, iter_xpath, funcion_print=eprint)
                                            eprint("[Procesada Alerta de EFTA sobre Acreditación]")
                                        else:
                                            eprint("[Problemas con alerta de EFTA sobre Acreditación]")
                                            checkDesacreditar = False

                                    except (ElementClickInterceptedException,ElementNotInteractableException) as e:
                                        raise ExcepcionDeMuestra("Error al cambiar acreditación (Reintentar)")
                            
                        else:
                            
                            for i in sorted(lista_alertas_pop, reverse=True):
                                del lista_alertas[i]

                            if len(lista_alertas) == 0:
                                eprint("[Sin alertas de Horas]")

                            else:
                                if checkCambiarFechas:
                                    TotalCambioFechas += 1
                                    eprint(f"[Fechas cambiadas]")

                                elif checkDesacreditar:
                                    flagDescargar = True #PROHIBIR PUBLICACION
                                    TotalDesacreditar +=1
                                    eprint(f"[Desacreditacion hecha]" if CorregirETFA else "[Muestra con alerta ETFA]")
                                
                                else:
                                    flagDescargar = True
                                    flagRutina = True
                                    
                    else:
                        flagRutina = True
                        flagDescargar = True
                        
                ###################################################
                #Revisar Controles Pendientes
                BotonSection(driver,"SectionRelatedSamples").click()
                EsperarCARGA_myLIMS(driver)
                
                cant_controles, controles_totales = ContarControlesPendientes(driver, ID_Actual=ID_Actual, funcion_print=logprint)

                if cant_controles != 0:
                    eprint(f"[{cant_controles} Controles Pendientes]")
                    flagControles = True

                if flagRutina or flagControles:
                    flagDescargar = True

                ###################################################
                #Intentar Publicar y continuar
                if not flagDescargar:

                    if AutoPublicar:
                        Publicar = MuestraPublicar(driver, ID_Actual, url=myLIMSdomain ,kill=True, funcion_print=logprint)

                        if Publicar == "Atraso":
                            eprint("[Atraso - No Publica]")
                            if Registrar:  
                                fila_muestra = [ id_excel, ID_Actual, "ATRASO", "ATRASO", "ATRASO", ""]
                                FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                            
                            timer.save(MuestraIndice)
                            break

                        if Publicar and Publicar != "Atraso":
                            TotalPublicados += 1
                            eprint("[Publica]\n")
                            if Registrar:  
                                fila_muestra = [ id_excel, ID_Actual, "PUBLICA", "PUBLICA", "PUBLICA", ""]
                                FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                                AgregarMuestraXLSX(dirExcel=dirExcelHistorico, ID_Muestra=ID_Actual, colnames=nombre_columnas)
                            
                            timer.save(MuestraIndice)
                            break

                        if not Publicar and Publicar != "Atraso":
                            eprint("[No Publica]")
                    
                    else:
                        TotalPublicados += 1
                        eprint("[Publicable]\n")
                        if Registrar:  
                            fila_muestra = [ id_excel, ID_Actual, "PUBLICABLE", "PUBLICABLE", "PUBLICABLE", ""]
                            FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                        
                        timer.save(MuestraIndice)
                        break
                
                tiene_rutina = "NO" if not flagRutina else "SI"
                tiene_controles = "NO" if not flagControles else "SI"
                
                if CorregirETFA:
                    if flagDesacreditar:
                        tiene_ETFA = "NO CORRIGE" if not checkDesacreditar else "CORREGIDO"
                    else:
                        tiene_ETFA = "NO"
                else: 
                    tiene_ETFA = "NO" if not flagDesacreditar else "SI"

                TotalDescarga += 1

                if Registrar:
                    fila_muestra = [ id_excel, ID_Actual, tiene_controles, tiene_rutina, tiene_ETFA, "DESCARGA PUBLICADA" if muestra_estado == "Publicada" else ""]
                    FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)
                
                if SoloBuscarControles:
                    eprint("[Saltada]\n")

                else:
                    eprint("[Descarga]\n")
                    BotonSection(driver,"SectionDetails").click()

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
                        eprint("Se encontraron varios botones de descarga...")
                        notify(title="Descarga Muestras", body=f"Se encontraron varios botones de descarga")

                    if obj_botones == 0:
                        raise ExcepcionDeCarga(f"No se encontró boton en la lista ({IDbotonesDocumentos}) para descargar documento (ID de botones disponibles en myLIMS: {id_botones_myLIMS})")
                    
                    logprint(f"Descargando con boton {IDboton}")
                    
                    EsperarCLICK(driver,atributo="data-test",valor=f"DocumentsButtonItem-DocTemplateId:{IDboton}", kill=True)
                    EsperarCARGA_myLIMS(driver, funcion_print=eprint, reintentos=30, kill=True)

                    #Desaparece barra naranja
                    for _ in range(timeout):
                        if queue_redy(driver): break
                        if alerta_visible(driver): raise ExcepcionDeMuestra("ALERTA en procesado de muestra (Reintentar)")
                        sleep(1)

                    else:
                        raise ExcepcionDeMuestra("TIMOUT en procesado de muestra (notificacion naranja no desaparece)")
                    sleep(1)
                    #Esperar descarga de documento revisando cantidad de archivos en carpeta
                    for _ in range(timeout):
                        if cant_previa == len(os.listdir(dir_Descargados)):
                            sleep(1)
                            continue
                        
                        if any(".crdownload" in archivo or ".part" in archivo for archivo in os.listdir(dir_Descargados)):
                            sleep(1)
                            continue

                        if alerta_visible(driver): raise ExcepcionDeMuestra("ERROR en procesado de muestra (Reintentar)")
                        TotalDescarga += 1
                        break

                    else:
                        raise ExcepcionDeCarga("No se ha descargado documento (Cantidad de archivos)")

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
                        elif not flagRutina and flagControles:
                            os.rename(dir_archivo, os.path.join(dir_CONTROLES,nombre_informe))
                        elif flagRutina and flagControles:
                            os.rename(dir_archivo, os.path.join(dir_AMBOS,nombre_informe))
                        else:
                            os.rename(dir_archivo, os.path.join(dir_OTROS,nombre_informe))

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
                        logprint("Probando conexión a internet")
                        internet_ok(timeout=1)
                        break
                    except (requests.ConnectionError, requests.exceptions.ReadTimeout):
                        eprint("No hay connexión a internet, reintentando cada 15 segundos...")
                        sleep(15)

                if isinstance(e, (ExcepcionDeMuestra,UnexpectedAlertPresentException, StaleElementReferenceException) ):
                    eprint(f'__________________\nProblemas con la muestra {ID_Actual}\n{FormatoExcepcion(e)}\n')
                
                elif isinstance(e, (InvalidSessionIdException, ExcepcionDeCarga) ):
                    eprint(f'__________________\nProblemas con la Navegador en la muestra {ID_Actual}\n{FormatoExcepcion(e)}\n')
                
                elif isinstance(e, ExcepcionArchivo):
                    eprint(f'__________________\nProblemas con archivo externo del programa en la muestra {ID_Actual}\n{FormatoExcepcion(e)}\n')
                
                elif isinstance(e, KeyError):
                    eprint(f'__________________\nProblemas Internos en el proceso con la muestra {ID_Actual}\n{FormatoExcepcion(e)}\n')
            
                else:
                    eprint(f'__________________\nProblemas desconocidos con la muestra {ID_Actual}\n{FormatoExcepcion(e)}\n')

                sleep(1)
                driver.refresh()
                EsperarCARGA_myLIMS(driver, funcion_print=eprint)
                IntentosDeCarga -= 1
                eprint(f'REINTENTANDO [{IntentosDeCarga} Intentos restantes]\n')
                continue
            
            timer.save(MuestraIndice)
            break

        else:
            notify(title=f"Problemas con la muestra {ID_Actual}!", body=type(Excepcion_error).__name__)

            eprint(f'SE ACABARON LOS INTENTOS\nsaltando muestra {ID_Actual}\n')
            timer.save(MuestraIndice)
            
            MuestrasError.append(ID_Actual)
            if Registrar:  
                fila_muestra = [ id_excel, ID_Actual, "ERROR", "ERROR", "ERROR", ""]
                FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                           
            MuestraIndice += 1
            continue
    
    timer.finish()
    id_excel += 1
    fila_muestra = [ id_excel, "----------", "----------", "----------", "----------", "----------" ]
    FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    

    notify(title="Programa terminado", body=f"Descarga de muestras finalizada!")

    Logout(driver,logout_url=Labsoftdomain)

    eprint("Sesión cerrada")
    driver.quit()
    timepo_ejecucion = f"{ ( (timer.end_time - timer.start_time)/3600):.2f}"

    if len(MuestrasError) != 0: eprint(f"Ocurrieron {len(MuestrasError)} errores\n")
        
    if BorrarDup and not SoloBuscarControles:

        borrados = False
        archivos_descargados = [f.name for f in Path(dir_Descargados).rglob('*') if f.is_file()]
        total_archivos = len(archivos_descargados)
        
        eprint(
            f'RESUMEN: Tiempo de ejecución: {timepo_ejecucion} horas\n\n'+
            f'Comenzó el {F_Inicial} y termino el {datetime.now().strftime("%d-%m %H:%M")} \n\n'+
            f'Existen {total_archivos} archivos en carpeta de descarga\n\n')

        eprint("Buscando duplicados para borrarlos\n")
        for PDFnombre in archivos_descargados:
            if "(" in PDFnombre and ")" in PDFnombre:
                borrados = True
                eprint(f'{PDFnombre} Duplicado...')
                os.remove(os.path.join(dir_Descargados, PDFnombre))
                total_archivos -= 1
                    
        if borrados: eprint("Duplicados borrados\n")
        else: eprint("Sin duplicados para borrar\n")
    
    summary = open(nombreRESUMEN,"w")
    if not SoloBuscarControles:
        summary.write(
            f"Resumen:\n\nTiempo de ejecucion: {timepo_ejecucion} horas\nComenzo el {F_Inicial} y termino el {datetime.now().strftime('%d-%m %H:%M')}\n"+
            f"{MuestrasCantidad} muestras en myLIMS\n"+
            f"{TotalDescarga} Descargados | {TotalPublicados} Publicados | {TotalCambioFechas} Fechas Cambiadas | {len(MuestrasError)} Errores\n"+
            f"{total_archivos} archivos dentro de directoro de Descarga\n\n"+
            f"Configuración Usada:\n\n----------------------\n")

    else:
        summary.write(
            f"Resumen:\n\nTiempo de ejecucion: {timepo_ejecucion} horas\nComenzo el {F_Inicial} y termino el {datetime.now().strftime('%d-%m %H:%M')}\n"+
            f"{MuestrasCantidad} muestras en myLIMS\n"+
            f"{TotalDescarga} Registrados | {TotalPublicados} Publicados | {TotalCambioFechas} Fechas Cambiadas | {len(MuestrasError)} Errores\n"+
            f"\n----------------------\nConfiguración Usada:\n")

    summary.write("  global_config:\n")
    for clave, valor in global_config.items():
        summary.write(f"    {clave}: {valor}\n")

    summary.write("\n  config:\n")
    for clave, valor in config.items():
        summary.write(f"    {clave}: {valor}\n")

    summary.close()
    eprint(f"Resumen guardado como {nombreRESUMEN}")
    exit(0)

except KeyboardInterrupt:
    print("Programa interrumpido por el usuario\nProceso del navegador desanclado\nCerrando terminal...")
    from time import sleep
    sleep(1)
    exit(1)