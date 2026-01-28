from __myLIMS_modulos__ import *
from datetime import time

def unique(lista, invertido=False):
    if invertido:
        return list(reversed(dict.fromkeys(list(lista))))
    else:    
        return list(dict.fromkeys(list(lista)))

def api_get(endpoint, token, api_url="https://hidrolab.mylimsweb.cloud/api/v2/"):
    #Enviar solicitud GET a la API
    out = requests.get(api_url+endpoint, 
                    headers = {
                        "Content-Type": "application/json",
                        "x-access-key": token
                    })
    return out.json()

#CERRAR SESIÓN
def Logout(driver, logout_url, kill=True):
    print("Cerrando sesion...\n")
    driver.get("https://hidrolab.mylimsweb.cloud/Default/SignOut")
    try:
        WebDriverWait(driver, 10).until(EC.url_contains(logout_url))
    except TimeoutException:
        if kill: raise ExcepcionDeMuestra(f'La sesión no se cerro correctamente (pagina labsoft no cargada)')
        else:
            print("La sesión no se cerró correctamente (pagina labsoft no cargada)")
            return 1


#INICIO DE SESIÓN
def Login(driver, path_internal, login_url, post_url, funcion_print=print):

    param = Config(RepositoryEnv(os.path.join(path_internal,"Param.env")))

    key = get('mylims_app', 'secret4')
    
    if key == None: 
        raise ExcepcionDeCarga(f'No se encontro llave de desencriptación. (Secret)')
    
    key = key.encode()

    encuser = param.get("USER").encode()
    encpasswd = param.get("PASSWD").encode()

    try:
        user = str(Fernet(key).decrypt(encuser).decode())
        passwd = str(Fernet(key).decrypt(encpasswd).decode())
        key = "\0" * len(key)

    except InvalidToken:
        raise ExcepcionDeCarga(f'Llave de desencriptación no coincide. (myLIMS_key)')
        
    try:
        #Cargar url principal de mylims y esperar que se rediriga a login
        driver.get(post_url)
    except WebDriverException as e:
        input(f"Error al inicial el navegador:\n{e}\nEnter para cerrar...")
        exit(1)

    AlternarMedidaVentana(driver)
    post_domain = post_url.split("/")[2]
    
    while post_domain in driver.current_url:
        try:
            #URL del login
            WebDriverWait(driver, 20).until( EC.url_contains(login_url) ) 
            
            #Elemento de login
            WebDriverWait(driver, 20).until( EC.presence_of_element_located((By.XPATH, '//*[@id="Username"]')) ) 
            
            sleep(1)
            break

        except TimeoutException:
            funcion_print(f'Elevado tiempo de espera para redirigir link {driver.current_url},\nReintentado...')
            driver.get(post_url)
            AlternarMedidaVentana(driver)

    try:
        
        driver.find_element(By.XPATH,'//*[@id="Username"]').send_keys(user)
        driver.find_element(By.XPATH,'//*[@id="Password"]').send_keys(passwd)

        driver.find_element(By.XPATH,'//*[@class="labsoft-login-button-primary"]').click()
        sleep(1)
        
    except NoSuchElementException as e:
        user = "\0" * len(user)
        passwd = "\0" * len(passwd)

        raise ExcepcionDeCarga(f'No se encuentran campos para rellenar contraseña: \npost_url: {post_url}\ncurrent: {driver.current_url}\nlogin: {login_url}\n\n{e}')

    user = "\0" * len(user)
    passwd = "\0" * len(passwd)

    if login_url in driver.current_url:
        raise ExcepcionDeCarga(f'Error en inicio de sesión, credenciales inválidas')

    if not forzar_carga(driver, url=post_url, funcion_print=funcion_print):
        raise ExcepcionDeCarga(f'Error interno de la página, no se cargó el link correctamente: {post_url}')

    try:
        _ = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ug-preview-hotspot-dismiss-text')]")))
        _.click()
    except TimeoutException:
        pass

#Revisar si carga la página y reintentar
def forzar_carga(driver, url, max_intentos=8, reintentos=4, funcion_print=print, kill=True):
  if url not in driver.current_url:
    driver.get(url)

  n_reintentos = 1 #Al cumplir numero de reintentos, devuelve verdadero
  intento = 0 #Si se alcanza el máximo, devuelve falso

  while n_reintentos != reintentos:   
    #print(f"Intento: {intento} var: {var}")

    if intento == max_intentos:
      funcion_print("Error al cargar la página, reintentos máximos alcanzados al forzar la carga")
      return False
        
    if "callback" in driver.current_url:
      #Redirección de backend, reintentando
      sleep(n_reintentos)
      driver.get(url)
      n_reintentos, intento = 1, intento + 1

    elif url in driver.current_url:
      #Bien, esperando redirección
      sleep(n_reintentos)
      n_reintentos, intento = n_reintentos + 1, intento + 1

    else:
      #Revisar link
      try:
        sleep(n_reintentos)
        if "Muitos usuários" in driver.find_element(By.XPATH,"//*[@id='message' and @class='alert alert-danger']").text:
          
          if kill: raise ExcepcionDeMuestra(f'ALERTA DE MUCHOS USUARIOS, se necesita esperar')
          else:
            funcion_print(f"ALERTA DE MUCHOS USUARIOS, se necesita esperar")
            return False
          
        n_reintentos, intento = 1, intento + 1

      except NoSuchElementException:
        driver.get(url)
        n_reintentos, intento = 1, intento + 1

      except Exception as e:
        if kill: raise ExcepcionDeMuestra(f'Error al iniciar myLIMS, fallo en inicio de sesión\nExcepción: {e}')
        else:
            funcion_print(f"Alerta en myLIMS, fallo en inicio de sesión\nExcepción: {e}")
            return False
  
  return True


#Publicar control y devolver boleano indicado estado de publicación, si es atraso entonces devolver "ATRASO" (Verdad)
def MuestraPublicar(driver, ID_Muestra, url, kill=False, funcion_print=print, retry=True):
    
    x_path_alerta = "//*/div[contains(@class,'k-window') and contains(@style,'display: block;')]"
    
    driver.get(url+"Main.cshtml#Sample/Publish/"+str(ID_Muestra))
    EsperarCARGA_myLIMS(driver)

    if "Details" in driver.current_url:
        funcion_print("Muestra publicada desde antes (url)")
        EsperarCLICK(driver, atributo="data-test", valor="PublishCancelButton", kill=False)
        return False

    EsperarCLICK(driver, atributo="data-test", valor="PublishSaveButton", kill=kill)
    EsperarCARGA_myLIMS(driver)

    try: 
        #Esperar presencia de alertas
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, x_path_alerta)))

    #Sin alerta
    except TimeoutException:
        pass
    
    #Apareció alerta
    else:
        alertas = driver.find_elements(By.XPATH, x_path_alerta)
        
        if len(alertas) != 2:
            ventanas = alertas
        
        else:
            funcion_print(f"Se encontraron 2 alertas")

            primera_alerta = ""
            segunda_alerta = ""

            for alerta in alertas:
                estilo = alerta.find_element(By.XPATH,"./div[2]").get_attribute("style")

                if "overflow: unset;" in estilo:
                    segunda_alerta = alerta
                else:
                    primera_alerta = alerta 
            
            if primera_alerta == "" or segunda_alerta == "":
                raise ExcepcionDeMuestra("No se pudieron ordenar las alertas")

            ventanas = [primera_alerta, segunda_alerta]

        for idx,ventana in enumerate(ventanas):
            titulo = ventana.find_element(By.CLASS_NAME,"k-window-title").text
            descripcion = ventana.find_element(By.XPATH,".//div[@class='row labsoft-ui-layoutrow']/div[2]/div").text

            funcion_print(f"[{idx+1} ]ALERTA CON:\n\tTitulo: {titulo}\n\tDescripcion: {descripcion}\n")        

        if len(alertas) > 2:
            raise ExcepcionDeMuestra("Se encontraron más de 2 alertas activas")
        
        devolver = True

        #RECORRER VENTANAS
        for ventana in ventanas:

            titulo = ventana.find_element(By.CLASS_NAME,"k-window-title").text
            descripcion = ventana.find_element(By.XPATH,".//div[@class='row labsoft-ui-layoutrow']/div[2]/div").text
            
            ###
            if titulo == "Confirme":
                ventana.find_element(By.XPATH, '//*[@data-test="Confirmar"]').click()
                EsperarCARGA_myLIMS(driver)

            ###
            elif titulo == "Aviso":

                if SiExisteElemento(ventana,"data-test","Ok"):
                    EsperarCLICK(ventana, atributo="data-test", valor="Ok")
                    EsperarCARGA_myLIMS(driver)
                    
                elif SiExisteElemento(ventana,"data-test","No"):
                    EsperarCLICK(ventana, atributo="data-test", valor="No")
                    EsperarCARGA_myLIMS(driver)

                else:
                    raise ExcepcionDeMuestra("No se encontró boton para cancelar")
                
                devolver = False

            ###
            elif titulo == "Alerta":
                EsperarCLICK(ventana, atributo="data-test", valor="Ok")
                EsperarCARGA_myLIMS(driver)
                
                devolver = "Atraso"
            
            ###
            else:
                raise ExcepcionDeMuestra("Ventana excepcional")
            
        
        if devolver == "Atraso" or devolver == False:
            try:
                BotonSection(driver, "PublishCancelButton").click()

            except Exception as e:
                ExcepcionDeMuestra(f"No se ha podido cancelar la publicación [{devolver}]\nBoton cancelar: {e}")
        
    #Esperar concluir la publicacion
    try:
        WebDriverWait(driver, 120).until(EC.url_contains("Details"))

    except TimeoutException:
        funcion_print("Elevado tiempo de espera para publicar, recargando...")
        EsperarCLICK(driver, atributo="data-test", valor="PublishCancelButton", kill=False)

        if retry:
            return MuestraPublicar(driver, ID_Muestra=ID_Muestra, url=url, kill=kill, retry=False)
        else:
            raise ExcepcionDeMuestra("Elevado tiempo de espera para recargar, no se pudo publicar muestra")
        
    else:
        funcion_print("Muestra publicada con éxito")
        return True


#Devolver lista con elementos necesarios de muestras en Grid
def SampleRecon(driver, Excluido, CentroServicio, funcion_print=print):
    nMuestras = driver.find_element(By.CLASS_NAME, "k-pager-info").text
    ActualSample = []

    if nMuestras != "Nada a enseñar.":
        nMuestras = int(nMuestras.split("de")[1].split(" ")[1])
    else:
        return ActualSample

    if nMuestras != 0:
        funcion_print(f'Se encontraron {nMuestras} muestras\n')

        grid = driver.find_element(By.XPATH,'//*[contains(@class,"myLIMSweb-nowrap-table-td")]/div[contains(@class,"k-grid-content")]/table[@role="grid"]')
        lista_muestras = grid.find_elements(By.TAG_NAME,"tr")
        largo_lista_muestras = len(lista_muestras)

        for idx, muestra in enumerate(lista_muestras):
            
            tipo_m      = muestra.find_element(By.XPATH,
                                               './td[@data-test="SampleItemGrid.SampleType.Identification"]').text
            Activo      = muestra.find_element(By.XPATH,
                                               './td[@data-test="SampleItemGrid.Active"]').text
            Estados     = muestra.find_element(By.XPATH,
                                               './td[@data-test="SampleItemGrid.CurrentStatus.SampleStatus.Identification"]').text
            ID_muestras = muestra.find_element(By.XPATH,
                                               './td[@data-test="SampleItemGrid.Id"]').text
            Cliente     = muestra.find_element(By.XPATH,
                                               './td[@data-test="SampleItemGrid.Account.Identification"]').text
            N_muestra   = muestra.find_element(By.XPATH,
                                               './td[@data-test="SampleItemGrid.ControlNumber"]').text
            C_servicio  = muestra.find_element(By.XPATH,
                                               './td[@data-test="SampleItemGrid.ServiceCenter.Identification"]').text
            A_servicio  = "-"
            #A_servicio  = muestra.find_element(By.XPATH,
            #                                   './td[@data-test="SampleItemGrid"]').text
            
            if Estados == "Finalizada":
                if Activo == "Si": 
                    if ".0" in N_muestra: 
                        if C_servicio in CentroServicio: 
                            if (ID_muestras not in Excluido): 

                                ActualSample.append({
                                    "INDICE":idx+1,
                                    "NUMERO":N_muestra,
                                    "ID":ID_muestras,
                                    "ESTADO":Estados,
                                    "ACTIVO":Activo,
                                    "CLIENTE":Cliente, 
                                    "TIPO":tipo_m,
                                    "AREA":A_servicio,
                                    })
                                funcion_print(f'Muestra {ID_muestras} agregada ({idx+1} de {largo_lista_muestras})')

                            else: funcion_print(f"Saltando muestra {ID_muestras} erronea ({idx+1} de {largo_lista_muestras}):\nID:{ID_muestras} - Muestra dentro de excel\n")
                        else: funcion_print(f"Saltando muestra {ID_muestras} erronea ({idx+1} de {largo_lista_muestras})\nID:{ID_muestras} - Centro Servicio: {C_servicio} ({CentroServicio})\n")
                    else: funcion_print(f"Saltando muestra {ID_muestras} erronea ({idx+1} de {largo_lista_muestras})\nID:{ID_muestras} - N_muestra sin .0: {N_muestra}\n")
                else: funcion_print(f"Saltando muestra {ID_muestras} erronea ({idx+1} de {largo_lista_muestras})\nID:{ID_muestras} - Activo: {Activo}\n")
            else: funcion_print(f"Saltando muestra {ID_muestras} erronea ({idx+1} de {largo_lista_muestras})\nID:{ID_muestras} - Estado: {Estados}\n")
        return ActualSample


def BuscarAlertas(driver, tipo_rutinas, tipo_horas, nombreAlertaETFA, funcion_print=print):
    flagRutina= False
    flagCambiarFecha = False
    flagDesacreditar = False

    control_grilla = driver.find_element(By.XPATH, "//div[@class='myLIMSweb-mail-list-item-box']/div[contains(@class, 'k-pager-wrap') and contains(@class, 'k-widget') and @data-role='pager' and @id='pager']")
    cantidad_alertas = control_grilla.find_element(By.XPATH, ".//span[@class='k-pager-info k-label']").text

    if cantidad_alertas == "Nada a enseñar.":
        return  [flagCambiarFecha, flagRutina, flagDesacreditar]
    else:
        cantidad_alertas =  int(Cortar(cantidad_alertas, "de ", " ítems"))

    if cantidad_alertas > 10:
        funcion_print(f"[Más de 10 alertas ({cantidad_alertas})]")
        return [True, True, True]

    else:
        ###################################################
        #Revisar mensajes
        xpath_mensajes = '//div[@class="myLIMSweb-mail-list-item-box"]//li[contains(@class, "list-group-item")]'

        for index, mensaje in enumerate(driver.find_elements(By.XPATH,xpath_mensajes)):

            m_tipo_upper    = mensaje.find_element(By.XPATH,'./div/div[3]').text
            m_tipo          = m_tipo_upper.lower()

            m_inicio        = mensaje.find_element(By.XPATH,'./div/div[2]/div[1]').text
            m_state         = mensaje.get_attribute("class")
            m_cuerpo        = mensaje.find_element(By.XPATH, './div/div[2]/div[2]').text

            if "Informe con alertas" in m_inicio and "Informe con alertas Analíticas / Formato" in m_cuerpo:
                continue

            if "inactive" in m_state:
                continue  
            
            if m_tipo in tipo_rutinas or m_tipo in tipo_horas:
                if "Alerta de horas" in m_inicio:
                    funcion_print(f"[Alerta de Horas]")
                    flagCambiarFecha = True
                else:
                    funcion_print(f"[Alerta de tipo \"{m_tipo_upper}\"]")
                    flagRutina = True

            if m_tipo == nombreAlertaETFA and "Alerta de horas - ETFA" in m_inicio:
                flagDesacreditar = True

    return [flagCambiarFecha, flagRutina, flagDesacreditar]

def ContarControlesPendientes(driver, ID_Actual, funcion_print=lambda *args, **kwargs: None):
    xpath_controles = "//div[@id='InterfaceContent']/div[@style='']//table[@role='grid']//tr"
    
    control_grilla = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']/div[@style='']//div[contains(@class, 'k-pager-wrap') and contains(@class, 'k-widget') and @data-role='pager']")
    cantidad_controles = control_grilla.find_element(By.XPATH, ".//span[@class='k-pager-info k-label']").text

    if cantidad_controles == "Nada a enseñar.": 
        return [ 0, ["-"] ]
    
    cantidad_controles =  int(Cortar(cantidad_controles, "de ", " ítems"))
    Saltos = 1
    
    n_pendientes = 0
    lista_controles = []

    for _ in range(Saltos):
        controles = driver.find_elements(By.XPATH,xpath_controles)[1:]
        
        for control in controles:
            control_nmuestra = control.find_element(By.XPATH,'./td[@data-test="RelatedSamplesGrid.ControlNumber"]').text
            control_id = control.find_element(By.XPATH,'./td[@data-test="RelatedSamplesGrid.Id"]').text
            control_estado = control.find_element(By.XPATH,'./td[@data-test="RelatedSamplesGrid.CurrentStatus.SampleStatus.Identification"]').text
            
            if control_estado != "Publicada":
            
                if control_id == str(ID_Actual):
                    funcion_print(f"Saltando muestra original {control_id} en estado {control_estado}")
                
                elif control_nmuestra.split("-")[1][0] != "1":
                    funcion_print(f"Saltando submuestra [{control_id}][{control_nmuestra}]")

                else:
                    funcion_print(f"Control {control_id} en estado {control_estado}!")
                    lista_controles.append(control_id)
                    n_pendientes += 1


        if _ != Saltos-1:
            EsperarCLICK(driver,atributo="class",valor="k-icon k-i-arrow-60-right")
            EsperarCARGA_myLIMS(driver)

    return [n_pendientes,lista_controles]


#Devolver lista con diccionario de Controles que no se encuentren publicados
def ControlRecon(driver,muestraInicial):

    BotonSection(driver,"SectionRelatedSamples").click()    
    EsperarCARGA_myLIMS(driver)

    mainInterface = WebDriverWait(driver, timeout=120).until(EC.presence_of_element_located((By.XPATH,'//*[@id="InterfaceContent"]')))

    #Borrar elementos hijos para encontrar grilla
    for elemento in mainInterface.find_elements(By.XPATH,"*"):
        if elemento.get_attribute("style") == "": continue
        driver.execute_script("var cagaste = arguments[0]; cagaste.parentNode.removeChild(cagaste);",elemento)

    sleep(.1)
    ntexto = driver.find_element(By.TAG_NAME,'tbody').find_element(
        By.XPATH,
        '//*[@class="k-pager-info k-label" and @style="visibility: visible;"]'
        ).text

    while ntexto == "Nada a enseñar.":
        print("Carga muy rapida")
        sleep(1.5)
        ntexto = driver.find_element(By.TAG_NAME,'tbody').find_element(By.XPATH,'//*[@class="k-pager-info k-label" and @style="visibility: visible;"]').text    

    ActualCQ = []
    # nControl = int(ntexto.split("de")[1].split(" ")[1])
    
    # if nControl > 100: 
    #     print(f'MUCHOS CONTROLES {nControl}')
    #     return [{   
    #         "ID"    :"MÁS DE 100 CONTROLES",
    #         "NUMERO":"MÁS DE 100 CONTROLES",
    #         "NOMBRE":"MÁS DE 100 CONTROLES",
    #         "ESTADO":"MÁS DE 100 CONTROLES"
    #     }]
    
    for control in driver.find_element(By.XPATH,
                                        '//div[contains(@class,"k-grid-content")]/table[@role="grid"]'
                                        ).find_elements(By.TAG_NAME,"tr"):
        
        ID_CQ = control.find_element(By.XPATH,
                                        './td[@data-test="RelatedSamplesGrid.Id"]').text
        N_CQ = control.find_element(By.XPATH,
                                        './td[@data-test="RelatedSamplesGrid.ControlNumber"]').text
        Estado = control.find_element(By.XPATH,
                                        './td[@data-test="RelatedSamplesGrid.CurrentStatus.SampleStatus.Identification"]').text
        Nombre = control.find_element(By.XPATH,
                                        './td[@data-test="RelatedSamplesGrid.SampleType.Identification"]').text

        if Estado != "Publicada" and ID_CQ != muestraInicial:
            print(f'Encontrado control {ID_CQ} en estado {Estado}, agregando...')
            ActualCQ.append({
                "ID":ID_CQ,
                "NUMERO":N_CQ,
                "NOMBRE":Nombre,
                "ESTADO":Estado
                })
        else:
            continue

    return ActualCQ

# Usar para copiar envases y encontrar muestras en coti
def GetTablaColumna(driver, xpath_tabla):
    elemento_tabla = driver.find_element(By.XPATH, xpath_tabla)
    lista_columnas_tabla = elemento_tabla.find_elements(By.XPATH,"./tr/th")
    
    tabla_dict = {}
    for idx, elemento_columna in enumerate(lista_columnas_tabla):
        tabla_dict = tabla_dict | {elemento_columna.text:idx} #Listar data-test? revisar tablas donde salto error

    return tabla_dict


#Subir ID de muestras en listaFichero a navegador buscando código de barra 
def SubirLista(driver,listaLista, funcion_print=print):
    
    EsperarCARGA_myLIMS(driver)
    CodigoDeBarra = driver.find_element(By.XPATH,'//*[@placeholder="Código de Barras"]')
    largo_indices = len(listaLista)
    
    timer = DeltaTimer(buffer_size=10)
    timer.start()

    for idx, _ID in enumerate(listaLista):
        timer.delta()
        timer.final(idx-1,largo_indices)
        
        CodigoDeBarra.click()
        CodigoDeBarra.send_keys(Keys.CONTROL, Keys.ARROW_LEFT)
        CodigoDeBarra.send_keys(Keys.CONTROL, Keys.DELETE)
        CodigoDeBarra.send_keys(str(_ID))
        CodigoDeBarra.send_keys(Keys.ENTER)
        try:
            WebDriverWait(driver, 3).until(
                EC.none_of(
                    EC.presence_of_element_located((By.CLASS_NAME,'inputError'))
                    ))
        except TimeoutException:
            funcion_print(f'Error con id: {_ID}\n')
            continue
        
        funcion_print(f"ID {str(_ID)} subido ({idx+1} de {largo_indices}) [restantes: {timer.t_restante} - final: {timer.end_time}]")
        EsperarCARGA_myLIMS(driver)


def obtener_delta(delta_texto):
    delta_num = int( re.findall( r'\d+', delta_texto )[0] )

    if "dias" in delta_texto or "días" in delta_texto:
        # delta_num = timedelta(days=delta_num-1, hours=randint(21,23), minutes=randint(1,59) )
        delta_num = timedelta(days=delta_num)
    if "horas" in delta_texto:
        delta_num = timedelta(hours=delta_num)
    
    if delta_texto == None:
        delta_num = timedelta(hours=0)
    
    if delta_texto != None and "dias" not in delta_texto and "días" not in delta_texto and "horas" not in delta_texto:
        raise ExcepcionDeMuestra(f"ERROR EN FORMATO, delta no reconocido [{delta_texto}]")
    
    return delta_num


def risdigit(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def fecha_aleatoria(minimo,maximo):
    if maximo > minimo:
        return datetime.fromtimestamp(uniform(minimo+1,maximo-1))
    
    if maximo < minimo:
        return datetime.fromtimestamp(uniform(maximo+1,minimo-1))
     
    if maximo == minimo:
        return datetime.fromtimestamp(maximo)

def FormatoLimiteHoras(inicio_jornada, extension_jornada):

    inicio_jornada = str(inicio_jornada)
    extension_jornada = str(extension_jornada)
    
    try:
        if ":" in inicio_jornada:
            di1 = datetime.strptime(inicio_jornada, "%H:%M")
        else:
            di1 = datetime.strptime(inicio_jornada , "%H")

        # Procesar extension_jornada
        if ":" in extension_jornada:
            e2 = datetime.strptime(extension_jornada, "%H:%M")
        else:
            e2 = datetime.strptime(extension_jornada, "%H")

    except ValueError as e:
        raise ExcepcionArchivo(f"Error de formato al intentar estimar la jornada laboral:\n{e}") 

    extension = timedelta(hours=e2.hour, minutes=e2.minute)

    # Sumar
    de2 = di1 + extension

    # if not risdigit(inicio_joranda) or not risdigit(extension_jornada):
        # raise ExcepcionDeCodigo(f"inicio de jornada o extencion no son convertibles a numeros! [{inicio_joranda}] [{extension_jornada}]") 

    #Jornadas Laborales
    return [ time(hour=di1.hour, minute=di1.minute ), time(hour=de2.hour, minute=de2.minute ) ]

def marg_random(): 
    return timedelta(hours=randint(0,2), minutes=randint(0,59))

def formato_fecha(fecha, formato="%d/%m/%Y %I:%M %p"):
    if fecha == None:
        return None
    
    if "/" in fecha:
        formato.replace("/", "-")
    elif "-" in fecha:
        formato.replace("-", "/")
    else:
        raise ExcepcionDeMuestra(f"Problemas al formatear la fecha {fecha}:\n{e}")

    try:
        if ".m." in fecha or "M" in fecha:

            if "a.m." in fecha:
                return datetime.strptime(fecha.replace("a.m.", "AM"), formato) 

            elif "p.m." in fecha:
                return datetime.strptime(fecha.replace("p.m.", "PM"), formato) 

            else:
                raise ExcepcionDeMuestra(f"Formato de fecha desconocido {fecha}")

        else:
            return datetime.strptime(fecha, formato.replace("%I:%M %p", "%H:%M"))
        
    except ValueError as e:
        raise ExcepcionDeMuestra(f"Problemas al formatear la fecha {fecha}:\n{e}")

def obtener_limites(jornada_inf, jornada_sup, cota_minima, cota_maxima):
    
    if cota_minima == None and cota_maxima == None:
        raise ExcepcionDeCodigo("ERROR EN CODIGO, cota_minima y cota_maxima no pueden estar vacías al mismo tiempo")
    
    min_hora     = cota_minima.time() if cota_minima is not None else None
    max_hora     = cota_maxima.time() if cota_maxima is not None else None

    inicio_jornada_hora = jornada_inf
    fin_jornada_hora    = jornada_sup

    if min_hora != None:
        if min_hora > fin_jornada_hora and min_hora < time(hour=23,minute=59,second=59): #19:30 - 23:50
            cota_minima += timedelta(days=1) # dia siguiente
            cota_minima = datetime.replace(cota_minima, hour=inicio_jornada_hora.hour, minute=inicio_jornada_hora.minute)
        if min_hora < inicio_jornada_hora and min_hora >= time(hour=00,minute=00,second=00): #00:00 - 8:30
            cota_minima = datetime.replace(cota_minima, hour=inicio_jornada_hora.hour, minute=inicio_jornada_hora.minute)

    if max_hora != None:
        if max_hora > fin_jornada_hora and max_hora < time(hour=23,minute=59,second=59): #19:30 - 23:50
            cota_maxima = datetime.replace(cota_maxima, hour=fin_jornada_hora.hour, minute=fin_jornada_hora.minute)

        if max_hora < inicio_jornada_hora and max_hora >= time(hour=00,minute=00,second=00): #00:00 - 8:30
            cota_maxima -= timedelta(days=1)  # dia anterior
            cota_maxima = datetime.replace(cota_maxima, hour=fin_jornada_hora.hour, minute=fin_jornada_hora.minute)

    if cota_minima != None and cota_maxima != None and cota_minima.timestamp() > cota_maxima.timestamp():
        raise ExcepcionDeMuestra(f"CASO CONFLICTIVO, favor de revisar muestra. La fecha de recepcion {cota_minima} es superior a la fecha limite {cota_maxima} y no se puede estimar nueva fecha.")
        
    return [cota_minima, cota_maxima]

def atrasar_fecha_laboral(fecha_muestreo, delta_texto, inicio_joranda, extension_jornada, cota_minima=None, cota_maxima=None, return_string=False, funcion_print=print):
    
    fecha_muestreo = formato_fecha(fecha_muestreo)

    #Limites de la muestra dados por el metodo y la fecha de muestreo
    cota_minima = formato_fecha(cota_minima)
    cota_maxima = formato_fecha(cota_maxima)

    delta = obtener_delta(delta_texto)
    fecha_limite  = fecha_muestreo + delta 
    
    lim_jornada_inicio, lim_jornada_fin = FormatoLimiteHoras(inicio_joranda, extension_jornada)
    lim_inferior, lim_superior  = obtener_limites(lim_jornada_inicio, lim_jornada_fin, cota_minima, cota_maxima)
    
    n = 0
    if lim_inferior != None and lim_superior != None:
        while True:
            nueva_fecha = fecha_aleatoria(lim_inferior.timestamp(), lim_superior.timestamp() )
            n+=1
            if (nueva_fecha.time() > lim_jornada_inicio and nueva_fecha.time() < lim_jornada_fin ) or nueva_fecha.time() == lim_jornada_fin:
                n = 0
                break
            if n%100 == 0: funcion_print(f"demorado en encontrar {nueva_fecha.time()} [{lim_inferior} - {lim_superior}] [ {lim_jornada_inicio} - {lim_jornada_fin}]")
            if n%1000 == 0: raise ExcepcionDeMuestra(f"Problemas con las horas, no se pudo comprobar la nueva fecha dentro de jornada laboral: {nueva_fecha}")
    
    if lim_inferior != None and lim_superior == None:
        while True:
            nueva_fecha = lim_inferior + marg_random()
            n+=1
            if (nueva_fecha.time() > lim_jornada_inicio and nueva_fecha.time() < lim_jornada_fin ) or nueva_fecha.time() == lim_jornada_fin:
                n = 0
                break
            if n%100 == 0: funcion_print(f"demorado en encontrar {nueva_fecha.time()} [{lim_inferior} - {lim_superior}] [ {lim_jornada_inicio} - {lim_jornada_fin}]")
            if n%1000 == 0: raise ExcepcionDeMuestra(f"Problemas con las horas, no se pudo comprobar la nueva fecha dentro de jornada laboral: {nueva_fecha}")
    
    if lim_inferior == None and lim_superior != None:
        while True:
            nueva_fecha = lim_superior - marg_random()
            n+=1
            if (nueva_fecha.time() > lim_jornada_inicio and nueva_fecha.time() < lim_jornada_fin ) or nueva_fecha.time() == lim_jornada_fin:
                n = 0
                break
            if n%100 == 0: funcion_print(f"demorado en encontrar {nueva_fecha.time()} [{lim_inferior} - {lim_superior}] [ {lim_jornada_inicio} - {lim_jornada_fin}]")
            if n%1000 == 0: raise ExcepcionDeMuestra(f"Problemas con las horas, no se pudo comprobar la nueva fecha dentro de jornada laboral: {nueva_fecha}")
    
    funcion_print(f"Fecha limite estimada: {fecha_limite}\n"+
                  f"Delta: {delta}\n"+
                  f"Limite Inferior: {lim_inferior}\n"+
                  f"Limite Superior: {lim_superior}\n"+
                  f"Nueva Fecha: {nueva_fecha.strftime('%d-%m-%Y %H:%M')}")

    if return_string:
        return nueva_fecha.strftime("%d-%m-%Y %H:%M")
    else:
        return nueva_fecha


#OBTENER DELTA CON MENOR HORAS
def limpiar_diccionario(diccionario_alertas):
    metodos_vistos = {}
    indices_repetidos = []

    for i, (indice, metodo) in enumerate([[alerta["index"], alerta["metodo"]] for alerta in diccionario_alertas]):
        if metodo in metodos_vistos:
            indices_repetidos.append([metodos_vistos[metodo], str(i+1)])
        else:
            metodos_vistos[metodo] = str(i+1)

    diccionario = {}
    for sublista in indices_repetidos:
        clave = sublista[0]
        if clave not in diccionario:
            diccionario[clave] = sublista
        else:
            diccionario[clave].extend(sublista[1:])

    indices_repetidos = list(diccionario.values())
    lista_fecha_incorrecta = []

    for lista_indices in indices_repetidos:
        lista_fecha_ciclo = []

        for index in lista_indices:
            fecha_de_alerta = formato_fecha(diccionario_alertas[int(index)-1]["fecha_base"])
            delta_num = obtener_delta(diccionario_alertas[int(index)-1]['delta'])
            lista_fecha_ciclo.append([str(index), fecha_de_alerta+delta_num ])

        indice, fecha_nueva = min(lista_fecha_ciclo, key=lambda item: item[1])
        lista_fecha_ciclo.remove([indice, fecha_nueva]) #Borrar la correcta para recorrer denuevo y eliminar resto
        indices_alertas_borrar = [lista_fecha_ciclo[i][0] for i in range(len(lista_fecha_ciclo))]
        lista_fecha_incorrecta += indices_alertas_borrar
    
    return [alerta for alerta in diccionario_alertas if alerta['index'] not in lista_fecha_incorrecta]

def Cortar(texto, inicio, final):
    return texto.split(inicio)[1].split(final)[0]

#Cambiar la fecha de inicio de la muestra dentro del url en myLIMS
def CambiarFechas(driver, alertas, inicio_joranda, extension_jornada, funcion_print=print):
    diccionario_alertas = []
    flag_estado = True
    alertas = unique(alertas)

    if "\'" not in choice(alertas):
        funcion_print("Alerta con formato antiguo, saltando revisión.")
        return False

    #BUSCANDO SIN ESTAR EN LA SECCION DE LA PAGINA WEB
    muestra_estado = driver.find_element(By.XPATH, "//div[@id='InterfaceContent']/div[1]/div[1]//div[5]/div[3]//input[@class='k-input']").get_attribute("value")
    if muestra_estado == "Publicada":
        funcion_print("Muestra ya publicada")
        return False
    
    if muestra_estado != "Finalizada":
        funcion_print(f"Saltando muestra con estado: {muestra_estado}.")
        return False
    
    fecha_muestreo = driver.find_element(By.XPATH, "//input[@data-test='TakenDateTime']").get_attribute("value").replace("-", "/")
    fecha_recepcion = None

    AlternarMedidaVentana(driver) #Cambiar tamaño para hacer click en "Historial"
    BotonSection(driver,"Historial").click()
    EsperarCARGA_myLIMS(driver)

    for fila in driver.find_elements(By.XPATH, '//div[@id="InterfaceContent"]/div[5]/div[@class="row labsoft-ui-layoutrow"]/div[1]//tbody[@role="rowgroup"]/tr'):
        if "Recibida" == fila.find_element(By.XPATH, './td[@data-test="StatusHistoryGrid.SampleStatus.Identification"]').text:
            fecha_recepcion = ":".join(fila.find_element(By.XPATH, './td[@data-test="StatusHistoryGrid.EditionDateTime"]').text.replace("-", "/").split(":")[:-1])

    #MISMO METODO DISTINTO PARAMETRO ENTONCES DELTA MÁS DESFAVORABLE
    for index, alerta in enumerate(alertas):
        dict_alerta = {}

        """
        dict_alerta = { index:
                        metodo:
                        alerta_texto:
                        fecha_recepcion:
                        fecha_base:
                        delta:
                        cota_minima:
                        cota_maxima:
                    }
        """

        #SAMPLE:
        #Error en hora inicio análisis: Color verdadero 'Visual-Color-Verdadero'.
        #Analito se debe reportar en 24 horas (Fecha límite Inicio Análisis 12/03/2024 18:50) 
        #y se está reportando con fecha 14/03/2024 10:39.
        
        # Error en hora inicio análisis: Turbiedad 'Nefelométrico'. 
        # Analito se debe reportar en 22 horas (Fecha límite Inicio Análisis 23/04/2024 11:22) 
        # y se está reportando con fecha 23/04/2024 11:30.

        #+3
        #Error en Fecha de Recepción para el análisis Color verdadero 'Visual-Color-Verdadero'. 
        #Analito se debe reportar en 24 horas desde la fecha de muestreo (12/03/2024 11:30) 
        #y la Fecha de Recepción de la muestra (14/03/2024 15:43) 
        #es posterior a la fecha límite del inicio del análisis (13/03/2024 14:30). 
        #Analito se debería reportar inmediatamente después de la fecha de recepción de la muestra..
        
        #INDICAR DELTA EN ALERTA
        #Error en hora inicio análisis: Cloruro 'Vol-Cl'. 
        #Fecha Inicio Análisis (05/04/2024 14:10) es anterior a fecha de recepción de la muestra (06/04/2024 09:00)
        
        #Error en hora inicio análisis de cálculo: Nitrógeno total 'NO2+NO3+NKT'. 
        #Analito se debe reportar después de Nitrato (13/03/2024 10:00), 
        #Nitrito (13/03/2024 11:00) y Nitrógeno total Kjeldahl (13/03/2024 15:02) 
        #y se está reportando con fecha 13/03/2024 13:09
        
        try:
            dict_alerta['index'] = str(index+1)
            div_comilla = alerta.split("\'")
            
            if "4,4" in div_comilla[0] and (" - DDT" in div_comilla[1] or " - DDD" in div_comilla[1] or " - DDE" in div_comilla[1]): dict_alerta['metodo'] = div_comilla[2]
            else: dict_alerta['metodo'] = div_comilla[1]
                
            dict_alerta['alerta_texto'] = alerta

            if "Error en hora inicio análisis" in alerta and "se debe reportar en" in alerta:
                dict_alerta['tipo'] = "Análisis reportado después de fecha limite"
                dict_alerta['fecha_recepcion'] = fecha_recepcion
                dict_alerta['fecha_base']  = fecha_muestreo

                dict_alerta['cota_minima'] = fecha_recepcion
                new_delta = Cortar(alerta, "Analito se debe reportar en ", " (" )
                
                #BUSCAR FORMATO DE DELTA ANTIGUO
                if "+3" in new_delta:
                    dict_alerta['delta'] = new_delta.replace("+3", "")
                    
                    new_hora_maxima = Cortar(alerta, "(Fecha límite Inicio Análisis ", ")") #Cuenta con +3
                    dict_alerta['cota_maxima'] = (formato_fecha(new_hora_maxima) + timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")
            

                else:
                    dict_alerta['delta'] = new_delta
                    dict_alerta['cota_maxima'] = Cortar(alerta, "(Fecha límite Inicio Análisis ", ")")

            if "Analito se debería reportar inmediatamente después de la fecha de recepción de la muestra" in alerta:
                dict_alerta['tipo'] = "Recepción atrasada, inicio inmediato"
                dict_alerta['fecha_recepcion'] = fecha_recepcion
                dict_alerta['fecha_base']  = dict_alerta['fecha_recepcion']
                dict_alerta['delta'] = "3 horas"
                dict_alerta['cota_minima'] = dict_alerta['fecha_base']
                dict_alerta['cota_maxima'] = None

            if "es anterior a fecha de recepción de la muestra" in alerta:
                dict_alerta['tipo'] = "Iniciada antes de recepción"
                dict_alerta['fecha_recepcion'] = fecha_recepcion
                dict_alerta['fecha_base']  = dict_alerta['fecha_recepcion']
                dict_alerta['delta'] = "3 horas"
                dict_alerta['cota_minima'] = dict_alerta['fecha_base']
                dict_alerta['cota_maxima'] = None
        
            if "análisis de cálculo" in alerta:
                dict_alerta['tipo'] = "Reportar después de análisis de cálculo"
                dict_alerta['fecha_recepcion'] = None
                dict_alerta['fecha_base']  = (max([formato_fecha(_.split(")")[0]) for _ in alerta.split("(")[1:]])).strftime("%d/%m/%Y %H:%M")
                dict_alerta['delta'] = "3 horas"
                dict_alerta['cota_minima'] = dict_alerta['fecha_base']
                dict_alerta['cota_maxima'] = None
            
            diccionario_alertas.append(dict_alerta)
        
        except IndexError:
            funcion_print("Error, alerta desconocida")
            return False
        
    diccionario_alertas = limpiar_diccionario(diccionario_alertas)

    for alerta in diccionario_alertas:

        fecha_base  = alerta['fecha_base']
        metodo      = alerta['metodo']
        delta_texto = alerta['delta']
        info_tipo   = alerta['tipo']

        funcion_print(f"\nAlerta: {alerta['alerta_texto']}\n\nTipo de muestra: {info_tipo} \n"+
                      f"Fecha Recepcion: {fecha_recepcion}\nFecha Base: {fecha_base}\nMetodo: {metodo}")
        
        nueva_fecha_inicio = atrasar_fecha_laboral(fecha_base, delta_texto, inicio_joranda=inicio_joranda, extension_jornada=extension_jornada, cota_maxima=alerta['cota_maxima'], cota_minima=alerta['cota_minima'], return_string=True, funcion_print=funcion_print)
        
        if nueva_fecha_inicio == fecha_recepcion:
            funcion_print(f"Nueva fecha de inicio es igual a la fecha de recepción, sumando 1 minuto")
            nueva_fecha_inicio = (datetime.strptime(nueva_fecha_inicio, "%d-%m-%Y %H:%M") + timedelta(minutes=1)).strftime("%d-%m-%Y %H:%M")
        
        AlternarMedidaVentana(driver) #Cambiar tamaño para hacer click en "Historial"

        BotonSection(driver,"Historial").click()
        EsperarCARGA_myLIMS(driver)

        filas = driver.find_elements(By.XPATH, '//div[@id="InterfaceContent"]//div[@class="row labsoft-ui-layoutrow"]/div[2]//table[@role="grid"]/tbody/tr')
        
        for idx,fila in enumerate(filas):
            
            row_metodo = fila.find_element(By.XPATH, './td[@data-test="StatusHistoryMethodsGrid.SampleMethod.Method.Identification"]').text
            row_status = fila.find_element(By.XPATH, './td[@data-test="StatusHistoryMethodsGrid.MethodStatus.Identification"]').text
            row_inicio = fila.find_element(By.XPATH, './td[@data-test="StatusHistoryMethodsGrid.StartDateTime"]')
            
            if metodo in row_metodo and "Análise" in row_status:

                row_inicio.click()
                BotonAccion(driver,"StartButton").click()
                EsperarCARGA_myLIMS(driver)

                ventana_entrada = driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//input[@data-role="datetimepicker"]')
                fecha_antigua = ventana_entrada.get_attribute('value')

                if "/" in fecha_antigua:
                    nuevo_formato = "%d/%m/%Y %I:%M %p"
                else:
                    nuevo_formato = "%d-%m-%Y %I:%M %p"
                    
                if ".m." in fecha_antigua:
                    nueva_fecha_inicio = datetime.strptime(nueva_fecha_inicio, "%d-%m-%Y %H:%M").strftime(nuevo_formato).replace("AM", "a.m.").replace("PM", "p.m.")
                    funcion_print(f"formato a.m. cambiado: {nueva_fecha_inicio}")
                        
                ventana_entrada.send_keys(Keys.CONTROL, "a")
                ventana_entrada.send_keys(Keys.DELETE)
                EsperarCARGA_myLIMS(driver)

                funcion_print(f"metodo: {metodo} - fecha antigua: {fecha_antigua} - nueva fecha inicio: {nueva_fecha_inicio}")
                ventana_entrada.send_keys(nueva_fecha_inicio)
                EsperarCARGA_myLIMS(driver)

                BotonVentana(driver,"ChangeMethodInitialButton").click()
                EsperarCARGA_myLIMS(driver)

                try:
                    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH,'//div[@class="k-widget k-window" and contains(@style, "display: block")]')))
                    
                    try:
                        # BotonVentana(driver,"CancelMethodStatusButton").click()
                        BotonVentana(driver,"Si").click() 
                        EsperarCARGA_myLIMS(driver)

                    except NoSuchElementException:
                        try:
                            funcion_print(f"[FLAG] No se acepta nueva fecha de inicio [{nueva_fecha_inicio}]")

                            BotonVentana(driver,"Ok").click() #Posible alerta de fecha no correspondiente
                            BotonVentana(driver,"CancelMethodStatusButton").click()

                        except NoSuchElementException:
                            raise ExcepcionDeMuestra("Alerta desconocida al cambiar inicio de metodo")

                        flag_estado = False
                        
                    
                except TimeoutException:
                    pass

                nueva_fecha_real = driver.find_element(By.XPATH, f'//div[@id="InterfaceContent"]//div[@class="row labsoft-ui-layoutrow"]/div[2]//table[@role="grid"]/tbody/tr[{idx+1}]/td[@data-test="StatusHistoryMethodsGrid.StartDateTime"]').text
                funcion_print(f"fecha mylims final: {nueva_fecha_real}")
                break

        else:
            funcion_print(f"[FLAG] No se encontró el método {metodo} en la grilla de la seccion Historial")
            flag_estado = False

    return flag_estado

def get_analito_dict(driver, metodos=[], analitos=[], funcion_print=print):

    xpath_lista_analitos = "//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr"
    muestras_analisis = []
    
    for idx, analito in enumerate(driver.find_elements(By.XPATH, xpath_lista_analitos)):
        an_analisis        = analito.find_element(By.XPATH,"./td[@data-test='AnalysisGrid.Info.Identification']").text
        an_metodo          = analito.find_element(By.XPATH,"./td[@data-test='AnalysisGrid.Method.Identification']").text
        an_medida          = analito.find_element(By.XPATH,"./td[@data-test='AnalysisGrid.MeasurementUnit.Identification']").text

        diccionario = {"id":idx+1, "analisis":an_analisis, "metodo":an_metodo, "medida":an_medida}
        
        if metodos and analitos:
            if an_metodo in metodos and an_analisis in analitos:
                muestras_analisis.append(diccionario)

        elif metodos or analitos:
            if an_metodo in metodos or an_analisis in analitos:
                muestras_analisis.append(diccionario) 
        else:
            muestras_analisis.append(diccionario) 

    return muestras_analisis


#####################################################
#LLAMAR AL ESTAR EN VENTANA ANALISIS EN MODO EDICION
def edit_alterar_por_metodo(driver, analito_dict, nuevo_metodo):
    
    if type(analito_dict) == list:

        grupos = defaultdict(list)
        for d in analito_dict: grupos[d["metodo"]].append(d)

        m_copias = [
            [
            # driver.find_element(
            #     By.XPATH,
            #     f"//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr[{y['id']}]"
            # )
            f"//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr[{y['id']}]"

            for y in x
            ]
            for x in list(grupos.values())
        ]

    elif type(analito_dict) == dict:

        m_copias = [[f"//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr[{analito_dict['id']}]"]]
    
    for m_copia in m_copias:

        m_copia_1 = driver.find_element(By.XPATH, f"{m_copia[0]}/td[1]")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", m_copia_1)
        m_copia_1.click()

        for _ in m_copia[1:]:
            driver.execute_script("arguments[0].setAttribute('class', 'k-alt k-state-selected');", driver.find_element(By.XPATH, _))
        
        try:
            BotonAccion(driver,"AnalysisAlterMethodButton").click()
            EsperarCARGA_myLIMS(driver)
        except ElementNotInteractableException:
            return -2
        
        ventana = driver.find_element(By.XPATH, "//div[@class='k-widget k-window' and contains(@style, 'display: block;')]/div[@data-role='window']")
        
        cuadro_busqueda = ventana.find_element(By.XPATH, ".//span[@data-field='Identification']//input[@aria-label='Identificación' and @type='text']")
        
        cuadro_busqueda.send_keys(nuevo_metodo)
        cuadro_busqueda.send_keys(Keys.ENTER)
        EsperarCARGA_myLIMS(driver)

        filas_ventana = ventana.find_elements(By.XPATH, ".//div[@data-role='grid']/div[contains(@class, 'k-grid-content')]/table/tbody/tr")
        
        for fila in filas_ventana:
            id_fila = fila.find_element(By.XPATH, "./td[1]")
            if id_fila.text == nuevo_metodo:
                id_fila.click()
                break

        else:
            ventana.find_element(By.XPATH, ".//button[@data-test='Cancelar']").click()                       
            EsperarCARGA_myLIMS(driver)
            return -1

        ventana.find_element(By.XPATH, ".//button[@data-test='Seleccionar']").click()
        EsperarCARGA_myLIMS(driver)

    return 0


def edit_eliminar_por_analisis_dict(driver, analisis):
    for fila_analito in driver.find_elements(By.XPATH, f"//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr"):
        
        analito = fila_analito.find_element(By.XPATH, "./td[@data-test='AnalysisGrid.Info.Identification']")
        metodo = fila_analito.find_element(By.XPATH, "./td[@data-test='AnalysisGrid.Method.Identification']")

        if analito.text == analisis["analisis"] and metodo.text == analisis["metodo"]:
            analito.click()
            try:
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable( (By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="AnalysisRemoveButton"]')) ).click()
                EsperarCARGA_myLIMS(driver)
                
                return 0
            except TimeoutException:
                BotonAccion(driver,"Cancelar").click()
                EsperarCARGA_myLIMS(driver)
                return -1
            break

    else:
        BotonAccion(driver,"Cancelar").click()
        EsperarCARGA_myLIMS(driver)
        return -2
        

def edit_eliminar_por_metodo_dict(driver, dict_metodo):
    for fila_analito in driver.find_elements(By.XPATH, f"//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr"):
        
        metodo = fila_analito.find_element(By.XPATH, "./td[@data-test='AnalysisGrid.Method.Identification']")

        if metodo.text == dict_metodo["metodo"]:
            try:
                metodo.click()
                WebDriverWait(driver, 1).until(EC.element_to_be_clickable( (By.XPATH,'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="AnalysisRemoveButton"]')) ).click()
                EsperarCARGA_myLIMS(driver)
                
                return 0
            except TimeoutException:
                BotonAccion(driver,"Cancelar").click()
                EsperarCARGA_myLIMS(driver)
                return -1
            
            except ElementClickInterceptedException:
                return -2
    else:
        BotonAccion(driver,"Cancelar").click()
        EsperarCARGA_myLIMS(driver)
        return -2


def edit_agregar_por_analisis_y_metodo(driver, nuevo_analito, metodo):

    driver.find_element(By.XPATH, f'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="AnalysisAddPerAnalysisButton"][1]').click()
    EsperarCARGA_myLIMS(driver)

    ventana = driver.find_element(By.XPATH, "//div[@class='k-widget k-window' and contains(@style, 'display: block;')]/div[@data-role='window']")
    
    #Agregar el primer elemento y esperar que aparezcan los analisis requerimientos
    cuadro_busqueda_analisis = ventana.find_element(By.XPATH, ".//span[@data-field='Info.Identification']//input[@aria-label='Identificación' and @type='text']")    
    cuadro_busqueda_analisis.send_keys(nuevo_analito)
    EsperarCARGA_myLIMS(driver)

    cuadro_busqueda_metodo = ventana.find_element(By.XPATH, ".//span[@data-field='Method.Identification']//input[@aria-label='Método de Análisis' and @type='text']")    
    cuadro_busqueda_metodo.send_keys(metodo)
    cuadro_busqueda_metodo.send_keys(Keys.ENTER)
    EsperarCARGA_myLIMS(driver)

    filas_ventana = ventana.find_elements(By.XPATH, ".//div[@data-role='grid']/div[contains(@class, 'k-grid-content')]/table/tbody/tr")
    
    #Agregar nuevo analito
    for fila in filas_ventana:
        id_fila = fila.find_element(By.XPATH, "./td[1]")
        metodo_fila = fila.find_element(By.XPATH, "./td[2]")
        if id_fila.text == nuevo_analito and metodo_fila.text == metodo:
            id_fila.click()
            break

    else:
        ventana.find_element(By.XPATH, ".//button[@data-test='Cancelar']").click()                       
        EsperarCARGA_myLIMS(driver)
        return -1

    ventana.find_element(By.XPATH, ".//button[@data-test='Seleccionar']").click()
    EsperarCARGA_myLIMS(driver)
    
    return 0


def edit_revisar_medida(driver, analito_dict, funcion_print=print):
    xpath_medida_tabla = f"//div[@id='InterfaceContent']/div[2]//div[@data-role='grid']/div[2]/table/tbody/tr[{analito_dict['id']}]/td[@data-test='AnalysisGrid.MeasurementUnit.Identification']"
    edit_medida = driver.find_element(By.XPATH, xpath_medida_tabla)
    
    if edit_medida.text == analito_dict["medida"]:
        return 1
    
    edit_medida.click()
    EsperarCARGA_myLIMS(driver)
    
    driver.find_element(By.XPATH, f"{xpath_medida_tabla}//span[@data-test='MeasurementUnit-search']").click()
    EsperarCARGA_myLIMS(driver)
    
    ventana = driver.find_element(By.XPATH, "//div[@class='k-widget k-window' and contains(@style, 'display: block;')]/div[@data-role='window']")
    
    cuadro_busqueda = ventana.find_element(By.XPATH, ".//span[@data-field='Identification']//input[@aria-label='Identificación' and @type='text']")
    cuadro_busqueda.send_keys(analito_dict["medida"])
    cuadro_busqueda.send_keys(Keys.ENTER)
    
    EsperarCARGA_myLIMS(driver)

    filas_ventana = ventana.find_elements(By.XPATH, ".//div[@data-role='grid']/div[contains(@class, 'k-grid-content')]/table/tbody/tr")
    
    for fila in filas_ventana:
        id_fila = fila.find_element(By.XPATH, "./td[1]")
        if id_fila.text == analito_dict["medida"]:
            id_fila.click()
            break
    
    else:
        ventana.find_element(By.XPATH, ".//button[@data-test='Cancelar']").click()                       
        EsperarCARGA_myLIMS(driver)
        return -1
    

    ventana.find_element(By.XPATH, ".//button[@data-test='Seleccionar']").click()
    EsperarCARGA_myLIMS(driver)
    
    try:
        driver.find_element(By.XPATH, "//div[@class='k-widget k-window' and contains(@style, 'display: block;')]/div[@data-role='window']//button[@data-test='Confirmar']").click()
        EsperarCARGA_myLIMS(driver)
    except NoSuchElementException: pass
    
    return 0


def edit_aprobar_logistica(driver, nuevos_metodos, funcion_print=print):
    
    for logistica in driver.find_elements(By.XPATH, f"//div[@id='InterfaceContent']/div[3]//div[@data-role='grid']/div[@class='k-grid-content k-auto-scrollable']//table/tbody/tr"):
        
        log_metodo = logistica.find_element(By.XPATH,"./td[@data-test='LogisticGrid.Method.Identification']")
        log_responsable = logistica.find_element(By.XPATH, "./td[@data-test='LogisticGrid.DistributionUser.Identification']")
        
        # funcion_print(f"{log_metodo} - {log_responsable}")

        if log_metodo.text in nuevos_metodos and log_responsable.text == "":
            funcion_print(f"Logistica con metodo {log_metodo.text} sin responsable, distribuyendo...")
            log_responsable.click()

            BotonAccion(driver, "DistributeAnalysesButton")
            EsperarCARGA_myLIMS(driver)
        
        if log_metodo.text not in nuevos_metodos and log_responsable.text == "":
            funcion_print(f"ALERTA: Logistica externa con metodo {log_metodo.text} no distribuida.")

    return 0