#ACTUALIZAR CHROMIUN CON https://download-chromium.appspot.com/
try:
    
    import sys,os
    from datetime import datetime

    file_name           =   os.path.basename(__file__)
    DM_wd               =   os.path.dirname(os.path.realpath(__file__))
    internal_lib        =   os.path.normpath(os.path.join(DM_wd,"..","internal_lib"))

    sys.path.insert(0, internal_lib)

    from __myLIMS_modulos__ import *
    from __myLIMS_wrappers__ import *
    from __ficheros_modulos__ import *

    ########################################
    #Inicialización de Config
    ########################################

    try:
        config              =   GetConfig( dirConfig=os.path.join(DM_wd,"config.txt") )
        global_config       =   GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )

        timeout             =   120
        timeout_con_check   =   3

        nombreLOG       =   os.path.join(DM_wd,"log",datetime.now().strftime('reporte_%Y_%m_%d-%H_%M'))
        nombreRESUMEN   =   f"{nombreLOG}_RESUMEN.txt"
    
        try:
            
            myLIMSdomain        =   global_config["myLIMSdomain"] 
            Labsoftdomain       =   global_config["Labsoftdomain"]
            
            paisActual          =   global_config["paisActual"].replace("é","e").replace("ú","u").lower()
            log                 =   global_config["ActivarLOG"]

            INICIO_JORNADA      =   global_config["InicioJornada"]
            EXTENSION_JORNADA   =   global_config["ExtensionJornada"]
            
            tipo_rutinas        =   global_config["ListaMensajesRutina"].lower().split(",")
            tipo_horas          =   global_config["ListaMensajesHoras"].lower().split(",")

            filtroActual            =   config["filtro"].replace("é","e").replace("ú","u").lower()

            SoloBuscarControles     =   config["SoloBuscarControles"]
            DescargarPublicadas     =   config["DescargarPublicadas"]

            Registrar               =   config["RegistrarMuestras"]
            RevisarRutinas          =   config["RevisarRutinas"]
            AutoPublicar            =   config["AutoPublicar"]
            Olvidar                 =   config["Olvidar"]
            
            BorrarDup               =   config["BorrarDuplicados"]
            Alerta                  =   config["Alerta"]

            id_etfa_config          =   str(config["DOC_REVISION_ETFA_ID_CL"]).split(",")
            id_no_etfa_config       =   str(config["DOC_REVISION_ID_CL"]).split(",")
            
            nombreExcelRegistro     =   config["nombreExcelRegistro"]
            dirExcelRegistro        =   os.path.join(DM_wd, nombreExcelRegistro)
            
            nombreHistorico         =   config["nombreExcelHistorico"]
            dirExcelHistorico       =   os.path.join(DM_wd, nombreHistorico)

            nombreExcepciones       =   global_config["nombreExcelExcepciones"]
            dirExcepciones          =   os.path.join(internal_lib, nombreExcepciones)
        
        except KeyError as e:
            input(f"Error en archivo de configuración, falta el valor de {e}\n\nEnter para cerrar...")
            exit(1)

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
            
        driver = Chrome(options=DriverOptions)

        eprint("Iniciando sesión en labsoft\n")

        try:
            Login(driver, path_internal=internal_lib, post_url=mainUrl, login_url=Labsoftdomain)
            EsperarCARGA_myLIMS(driver, funcion_print=eprint, recargar=False)

        except ExcepcionDeCarga as e:
            eprint(f"{e}\n")
            input("Enter para cerrar...")
            exit(1)

    except Exception as e:
        notify(title="Problemas en programa", body=type(e).__name__)
        eprint(f"{FormatoExcepcion(e)}\nError al cargar myLIMS")
        input("Enter para cerrar navegador")
        Logout(driver,logout_url=Labsoftdomain)
        driver.quit()
        exit(1)

    ########################################
    #Busqueda ID de muestras a descargar
    try:
        driver.get(mainUrl)
        EsperarCARGA_myLIMS(driver, funcion_print=eprint, recargar=False)

        eprint(f"Cambiando los filtros de la Grilla, Cantidad de filtros: {len(filtros)}\n")
        EsperarCARGA_myLIMS(driver, funcion_print=eprint, recargar=False)

        ListaMuestras = []; MuestrasError = []

        for n_filtro in range(len(filtros)):
            
            for _ in range(3):
                try:

                    if n_filtro == 0:
                        BotonAccion(driver,"Grid").click()
                        EsperarCLICK(driver,atributo="data-test",valor="Exhibir Recuento")            
                    
                    filtro = filtros[n_filtro]

                    BotonAccion(driver,"Grid").click()
                    EsperarCLICK(driver,atributo="data-test",valor=filtro)
                    EsperarCARGA_myLIMS(driver, funcion_print=eprint, recargar=False)
                    
                    if pais == "BOG":
                        t_muestra_text = driver.find_element(By.XPATH,"//span[@data-test='SampleItemGridFilter.SampleType.Identification']//input[@type='text']")
                        t_muestra_text.send_keys("*agua")
                        t_muestra_text.send_keys(Keys.ENTER)
                        EsperarCARGA_myLIMS(driver)

                    control_grilla = driver.find_element(By.XPATH, "//div[contains(@class, 'k-pager-wrap') and contains(@class, 'k-widget') and @data-role='pager']")
                    control_grilla.find_element(By.XPATH, ".//span[@class='k-pager-sizes k-label']/span[1]").click()
                    EsperarCARGA_myLIMS(driver)

                    driver.find_element(By.XPATH, "//div[@class='k-animation-container']//ul[@class='k-list k-reset']/li[contains(text(), '100')]").click()
                    EsperarCARGA_myLIMS(driver)

                    break

                except ElementNotInteractableException:
                    driver.refresh()
                    
            else:
                eprint(f"[No se pudo configurar la grilla] (filtro o elementos por grilla)")
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()
                exit(1)

            MuestrasCantidad = control_grilla.find_element(By.XPATH, ".//span[@class='k-pager-info k-label']").text
            if MuestrasCantidad == "Nada a enseñar.":
                MuestrasCantidad = 0
                eprint(f"[No se encontraron muestras para el filtro {filtro}]")
                Logout(driver,logout_url=Labsoftdomain)
                driver.quit()
                exit(1)
            else:    
                MuestrasCantidad = int(Cortar(MuestrasCantidad, "de ", " ítems"))
                if MuestrasCantidad%100 == 0:
                    Saltos = int( MuestrasCantidad/100 )
                else:
                    Saltos = int( ( MuestrasCantidad/100 ) + 1 )
            eprint(f'Se registrarán { MuestrasCantidad } muestras en myLIMS para el filtro [{filtro}]\n')

            #BUSQUEDA DE ID PARA CADA PÁGINA
            for _ in range(Saltos):

                #Lista con los id de todas las muestras en grid actual
                ID_Muestras = [__.text for __ in WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((By.XPATH,'//*[@data-test="SampleItemGrid.Id"]')))]
                eprint(f'Página {_+1} registrada')
                
                ListaMuestras = ListaMuestras + [_ for _ in ID_Muestras if _ not in ID_Excluidos]
            
                if _ != Saltos-1: EsperarCLICK(driver,atributo="class",valor="k-icon k-i-arrow-60-right")
                EsperarCARGA_myLIMS(driver, funcion_print=eprint)

            else:            
                eprint("",end="\n")

        MuestrasCantidad = len(ListaMuestras)
        TotalDescarga = 0
        
        if not AutoPublicar: TotalPublicados = "Desactivado"
        else: TotalPublicados = 0

        if not RevisarRutinas: TotalCambioFechas = "Desactivado"
        else: TotalCambioFechas = 0

        T_MuestraInicio = None; T_TotalRestante = 0
        T_TotalInicio = int(tiempo())

        if SoloBuscarControles:
            eprint(f'Se agregaron {MuestrasCantidad} muestras a la cola, revisando controles y fechas para publicar...')
        else:
            eprint(f'Se agregaron {MuestrasCantidad} muestras a la cola, descargando...')

        minutosXmuestra = []

    except Exception as e:
        notify(title="Problemas en programa", body=type(e).__name__)
        eprint(f"{FormatoExcepcion(e)}\nOcurrió un error al obtener los ID de muestras, favor de revisar log")
        input("Enter para cerrar sesión y navegador")
        Logout(driver,logout_url=Labsoftdomain)
        wait(3)
        driver.quit()
        exit(1)

    id_excel = ObtenerIDExcel(dirExcel=dirExcelRegistro, ncol=0, colnames=nombre_columnas_reg)

    id_excel += 1
    fila_muestra = [ id_excel, "##########", "##########", "##########", datetime.now().strftime('[%d-%m-%Y %H:%M]')]
    FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    

    ########################################
    #Instancia para cada muestra a descargar
    for MuestraIndice, ID_Actual in enumerate(ListaMuestras,1):
        slog()
        id_excel += 1

        Excepcion_error = ""
        IntentosDeCarga = 5

        if not SoloBuscarControles:
            cant_previa = len(os.listdir(dir_Descargados))
        else:
            cant_previa = 0

        while IntentosDeCarga != 0:
            try: 
                T_MuestraInicio = tiempo()

                mxm = sum(minutosXmuestra)/len(minutosXmuestra)
                T_TotalRestante = mxm*(MuestrasCantidad-MuestraIndice)

                if int(mxm) == 0:
                    mxm = f"{mxm*60*60:.2f} seg/m"
                else:
                    mxm = f"{mxm*60:.2f} min/m"

                
                if int(T_TotalRestante) == 0: 
                    T_TotalRestante = f"{T_TotalRestante*60:.2f} minutos [{mxm}]"
                else:
                    T_TotalRestante = f"{T_TotalRestante:.2f} horas [{mxm}]"
                
            except ZeroDivisionError: 
                pass

            #Reintentar y recargar solo esta sección
            try:

                flagDescargar = False
                flagCambiarFecha = False
                flagRutina = False
                flagControles = False
                
                ChequearNavegador(driver, kill=True)

                driver.get(f"{myLIMSdomain}Main.cshtml#Sample/Details/{ID_Actual}")
                EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)

                N_Muestra = driver.find_element(By.XPATH, '//input[@data-test="ControlNumber"]').get_attribute("value")
                cliente = driver.find_element(By.XPATH, '//input[@data-bind="value: Account.Identification"]').get_attribute("value")
                
                if SoloBuscarControles:
                    eprint( f'\nRevisando ID: {ID_Actual}\n'+
                            f'N de Muestra: {N_Muestra}\n'+
                            f'Tiempo restante: {T_TotalRestante}\n'+
                            f'Muestras Restantes: {MuestrasCantidad-MuestraIndice} Muestras [{MuestraIndice}/{MuestrasCantidad}]\n'+
                            f'Registradas: {TotalDescarga} - Publicadas: {TotalPublicados} - Cambios de Fechas: {TotalCambioFechas}')
                else:
                    eprint( f'\nRevisando ID: {ID_Actual}\n'+
                            f'N de Muestra: {N_Muestra}\n'+
                            f'Tiempo restante: {T_TotalRestante}\n'+
                            f'Muestras Restantes: {MuestrasCantidad-MuestraIndice} Muestras [{MuestraIndice}/{MuestrasCantidad}]\n'+
                            f'Descargadas: {TotalDescarga} - Publicadas: {TotalPublicados} - Cambios de Fechas: {TotalCambioFechas}')

                muestra_estado = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']/div[1]/div[1]//div[5]/div[3]//input[@class='k-input']").get_attribute("value")
                
                if muestra_estado == "Publicada":
                    eprint("[Previamente Publicada]\n")

                    if not DescargarPublicadas: 
                        fila_muestra = [ id_excel, ID_Actual, "YA PUBLICADA", "YA PUBLICADA", ""]
                        FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                        AgregarMuestraXLSX(dirExcel=dirExcelHistorico, ID_Muestra=ID_Actual, colnames=nombre_columnas)
                        break
                    else:
                        flagDescargar = True
                        
                BotonSection(driver,"SectionMessage").click()
                EsperarCARGA_myLIMS(driver, funcion_print=eprint, kill=True)

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
                                        BotonSection(driver,"SectionMessage").click()
                                        EsperarCARGA_myLIMS(driver)

                                        driver.find_element(By.XPATH, iter_xpath).click()
                                        EsperarCARGA_myLIMS(driver, funcion_print=eprint)

                                        BotonAccion(driver,"Inactivar").click()
                                        EsperarCARGA_myLIMS(driver, funcion_print=eprint)

                                        driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//textarea[@class="k-textbox"]').send_keys("Corregido")
                                        BotonVentana(driver,"Confirmar").click()
                                        EsperarCARGA_myLIMS(driver, funcion_print=eprint)

                                        eprint("[Procesada Alerta de Horas]")

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
                                    flagRutina = True


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
                                fila_muestra = [ id_excel, ID_Actual, "ATRASO", "ATRASO", ""]
                                FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                            
                            minutosXmuestra.append( (int(tiempo())-int(T_MuestraInicio))/3600 )
                            break

                        if Publicar and Publicar != "Atraso":
                            TotalPublicados += 1
                            eprint("[Publica]\n")
                            if Registrar:  
                                fila_muestra = [ id_excel, ID_Actual, "PUBLICA", "PUBLICA", ""]
                                FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                                AgregarMuestraXLSX(dirExcel=dirExcelHistorico, ID_Muestra=ID_Actual, colnames=nombre_columnas)
                            
                            minutosXmuestra.append( (int(tiempo())-int(T_MuestraInicio))/3600 )
                            break

                        if not Publicar and Publicar != "Atraso":
                            eprint("[No Publica]")
                    
                    else:
                        eprint("[Publicable]\n")
                        if Registrar:  
                            fila_muestra = [ id_excel, ID_Actual, "PUBLICABLE", "PUBLICABLE", ""]
                            FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                        
                        minutosXmuestra.append( (int(tiempo())-int(T_MuestraInicio))/3600 )
                        break
                
                tiene_rutina = "NO" if not flagRutina else "SI"
                tiene_controles = "NO" if not flagControles else "SI"
                TotalDescarga += 1

                if Registrar:
                    if muestra_estado == "Publicada": fila_muestra = [ id_excel, ID_Actual, tiene_controles, tiene_rutina, "DESCARGA PUBLICADA"]
                    else: fila_muestra = [ id_excel, ID_Actual, tiene_controles, tiene_rutina, ""]
                    FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)
                
                if SoloBuscarControles:
                    eprint("[Saltada - Descargable]\n")

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
                        requests.head("https://8.8.8.8", timeout=timeout_con_check)
                        break
                    except (requests.ConnectionError, requests.exceptions.ReadTimeout):
                        eprint("No hay connexión a internet, reintentando cada 15 segundos...")
                        wait(15)

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

                wait(1)
                driver.refresh()
                EsperarCARGA_myLIMS(driver, funcion_print=eprint)
                IntentosDeCarga -= 1
                eprint(f'REINTENTANDO [{IntentosDeCarga} Intentos restantes]\n')
                continue
            
            minutosXmuestra.append( (int(tiempo())-int(T_MuestraInicio))/3600 )
            break

        else:
            notify(title=f"Problemas con la muestra {ID_Actual}!", body=type(Excepcion_error).__name__)

            eprint(f'SE ACABARON LOS INTENTOS\nsaltando muestra {ID_Actual}\n')
            minutosXmuestra.append((int(tiempo())-int(T_MuestraInicio))/3600)
            
            MuestrasError.append(ID_Actual)
            if Registrar:  
                fila_muestra = [ id_excel, ID_Actual, "ERROR", "ERROR", ""]
                FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    
                           
            MuestraIndice += 1
            continue
    
    id_excel += 1
    fila_muestra = [ id_excel, "----------", "----------", "----------", "----------" ]
    FilaAgregarXLSX(dirExcel=dirExcelRegistro, valores_fila=fila_muestra, colnames=nombre_columnas_reg, except_kill=False, except_create=True)                                    

    notify(title="Programa terminado", body=f"Descarga de muestras finalizada!")

    Logout(driver,logout_url=Labsoftdomain)

    eprint("Sesión cerrada")
    driver.quit()

    T_TotalFinal = int(tiempo())

    if len(MuestrasError) != 0: eprint(f"Ocurrieron {len(MuestrasError)} errores\n")
        
    if BorrarDup and not SoloBuscarControles:

        borrados = False
        archivos_descargados = [f.name for f in Path(dir_Descargados).rglob('*') if f.is_file()]
        total_archivos = len(archivos_descargados)
        
        eprint(
            f'RESUMEN: Tiempo de ejecución: { ( (T_TotalFinal-T_TotalInicio)/3600):.2f} horas\n\n'+
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
            f"Resumen:\n\nTiempo de ejecucion: {((T_TotalFinal-T_TotalInicio)/3600):.2f} horas\n{(sum(minutosXmuestra)/len(minutosXmuestra))*60:.2f} minutos por muestra promedio\nComenzo el {F_Inicial} y termino el {datetime.now().strftime('%d-%m %H:%M')}\n"+
            f"{MuestrasCantidad} muestras en myLIMS\n"+
            f"{TotalDescarga} Descargados | {TotalPublicados} Publicados | {TotalCambioFechas} Fechas Cambiadas | {len(MuestrasError)} Errores\n"+
            f"{total_archivos} archivos dentro de directoro de Descarga\n\n"+
            f"Configuración Usada:\n\n----------------------\n")

    else:
        summary.write(
            f"Resumen:\n\nTiempo de ejecucion: {((T_TotalFinal-T_TotalInicio)/3600):.2f} horas\n{(sum(minutosXmuestra)/len(minutosXmuestra))*60:.2f} minutos por muestra promedio\nComenzo el {F_Inicial} y termino el {datetime.now().strftime('%d-%m %H:%M')}\n"+
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