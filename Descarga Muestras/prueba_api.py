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
        nombre_columnas_reg     =   ["ID", "ID MUESTRAS", "TIENE CONTROLES", "TIENE RUTINAS","MARCA"]

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
                f"Solo Buscar Controles [True]:\t{SoloBuscarControles}\n\n"+
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
                print(f"{str_alerta}\n")

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

        token = get('mylims_app', 'secret7')
        x = get_samples_id("account ne null and active eq true and endswith(controlnumber, '.0') and "+
                   "currentstatus/samplestatus/identification eq 'finalizada' and "+
                   "servicecenter/identification eq 'hidrolab scl'",
                   apidomain=api_url,
                   token=token,
                   funcion_print=eprint, 
                   )
        input(x)