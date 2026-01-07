try:
  import traceback
  from cryptography.fernet import InvalidToken
  from cryptography.fernet import Fernet
  from os.path import exists
  from decouple import * 
  from time import sleep as wait
  import keyring, json
  
  from selenium.webdriver.support import expected_conditions as EC
  from selenium.webdriver.support.wait import WebDriverWait
  from selenium.webdriver.chrome.options import Options
  from selenium.webdriver.common.by import By
  from selenium.common.exceptions import *
  from selenium.webdriver import Chrome
  
except ModuleNotFoundError as e:
  input(f"Modulos no instalados: {e}\nEnter para cerrar")
  exit(1)

mylims_url = "https://hidrolab.mylimsweb.cloud/"
labsoft_url = "https://labsoft-identitycenter-sts.mylimsweb.cloud/"

try:
    def forzar_carga(driver, url= mylims_url+"/Main.cshtml#WorkSpace", max_intentos=8, reintentos=4, kill=True):
      driver.get(url)
      n_reintentos = 1 #Al cumplir numero de reintentos, devuelve verdadero
      intento = 0 #Si se alcanza el máximo, devuelve falso

      while n_reintentos != reintentos:   
        #print(f"Intento: {intento} var: {var}")

        if intento == max_intentos:
          return False
            
        if "callback" in driver.current_url:
          #Redirección de backend, reintentando
          wait(n_reintentos)
          driver.get(url)
          n_reintentos = 1
          intento += 1

        elif driver.current_url == url:
          #Bien, esperando redirección
          wait(n_reintentos)
          n_reintentos, intento = n_reintentos + 1, intento + 1

        else:
          #Revisar link
          try:
            wait(n_reintentos)
            if "Muitos usuários" in driver.find_element(By.XPATH,"//*[@id='message' and @class='alert alert-danger']").text:
              print(f"ALERTA DE MUCHOS USUARIOS, se necesita esperar")
              return False
              
            n_reintentos, intento = 1, intento + 1

          except NoSuchElementException:
            driver.get(url)
            n_reintentos, intento = 1, intento + 1

          except Exception as e:
              print(f"Alerta en myLIMS, fallo en inicio de sesión\nExcepción: {e}")
              return False

      return True

    def EsperarCARGA_myLIMS(driver, reintentos=60, funcion_print=print, recargar=True, extra=None):
        for _ in range(5):    
            for _ in range(reintentos):
                wait(1) # 1 reintento por segundo
                try:
                    if 'pace-inactive' in driver.execute_script('return document.querySelector("body > div.pace").getAttribute("class");'):
                        if extra == None: return 0
                        else: wait(extra); return 0
                except JavascriptException:
                    pass
            
            if recargar: driver.refresh()
            wait(5)
        else:
            funcion_print("Timeout al esperar carga de myLIMS")
            return 1

    internal_lib =  os.path.join( os.path.dirname(os.path.realpath(__file__)),"..","internal_lib")
    env_file_path = os.path.join(internal_lib,"Param.env")

    if not exists(env_file_path):
      input("No se econtro archivo con credenciales. (Param.env)\nPresione enter para cerrar")
      exit(1)

    config = Config(RepositoryEnv(env_file_path))

    # key = os.environ.get("myLIMS_key").encode()
    key = keyring.get_password('mylims_app', 'secret4')
    
    if key != None: key = key.encode()
    else:
      input("No se econtro llave de desencriptación. (myLIMS_key)\nPresione enter para cerrar")
      exit(1)

    encuser = config.get("USER").encode()
    encpasswd = config.get("PASSWD").encode()
    etiqueta = config.get("ETIQUETA")

    try:
      user = str(Fernet(key).decrypt(encuser).decode())
      passwd = str(Fernet(key).decrypt(encpasswd).decode())

    except InvalidToken as e:
      input(f"Llave de desencriptación no coincide. (myLIMS_key)\n{e}\nPresione enter para cerrar")
      exit(1)

    x = ""
    if keyring.get_password('mylims_app', 'secret7') != None:
      print("Token de acceso existente")
      x = str(input("Volver a registrar token de acceso? (s/N) "))

    DriverOptions = Options()
    DriverOptions.add_argument("--window-size=1172,708")
    DriverOptions.add_argument("--log-level=3")
    DriverOptions.add_argument('--force-dark-mode')

    DriverOptions.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])

    prefs = {
        'profile.default_content_setting_values.automatic_downloads':1,
        "profile.password_manager_enabled": False,
        
        "profile.avatar_index":39,
        
        "devtools.preferences.currentDockState": "\"undocked\"",
        "credentials_enable_service": False,
        "browser.theme.color_variant2":1,
        "browser.theme.follows_system_colors": False,
        "browser.theme.user_color2": -16726017,
    }

    DriverOptions.add_argument("--window-size=1172,708")
    DriverOptions.add_argument('--log-level=3')
    DriverOptions.add_experimental_option("prefs",prefs)
    

    driver = Chrome(options=DriverOptions)
    #driver.minimize_window()

    print(f"Iniciando sesión en labsoft con \'{etiqueta}\'")
    driver.get(labsoft_url+"Account/Login?ReturnUrl=%2Fconnect%2Fauthorize%2Fcallback%3Fclient_id%3DmyLIMSweb_JQuery%26redirect_uri%3Dhttps%253A%252F%252Fhidrolab.mylimsweb.cloud%252Fcallback%252Findex%26response_type%3Dcode%26scope%3Dopenid%2520myLIMSweb_API_Create%2520myLIMSweb_API_Read%2520myLIMSweb_API_Update%2520myLIMSweb_API_Delete%2520DataViewer_API_Create%2520DataViewer_API_Read%2520DataViewer_API_Update%2520DataViewer_API_Delete%2520DataFactory_API_Create%2520DataFactory_API_Read%2520DataFactory_API_Update%2520DataFactory_API_Delete%26state%3D3f7710d7f8f54206ab43e2adb4373545%26code_challenge%3DomdhGcvw4OZtkZOX0FbtzxaFQQ82k9KoWdY-zQiq1Ok%26code_challenge_method%3DS256%26response_mode%3Dquery%26requesterClient%3Dhidrolab")

    driver.find_element(By.XPATH,'//*[@id="Username"]').send_keys(user)
    driver.find_element(By.XPATH,'//*[@id="Password"]').send_keys(passwd)

    driver.find_element(By.XPATH,'//*[@class="labsoft-login-button-primary"]').click()

    wait(2)

    if labsoft_url in driver.current_url:
      driver.quit()
      input("Error en inicio de sesión, credenciales invalidas\nPresione enter para cerrar")
      exit(1)

    print("Credenciales válidas, esperando carga de myLIMS")

    if not forzar_carga(driver):
      input("Error interno de la página, no se cargó mylims correctamente\nPresione enter para cerrar")
      exit(1)
    
    if x == "s":      

      EsperarCARGA_myLIMS(driver)
      print("Extrayendo token de acceso")
      
      driver.get(mylims_url+"api/v2/IntegrationTokens/6")
      salida_json = json.loads(driver.find_element(By.XPATH,"//*").text)
      
      if salida_json["Identification"].replace("ó","o") != "Integracion de procesos":
        input(f"Error, índice de token de integración no corresponde: {salida_json['Identification']}")
        exit(1)
      else:
        keyring.set_password("mylims_app", "secret7", salida_json["Token"])
        print(f"Token de integración guardado correctamente \"{salida_json['Identification']}\"")

    print("myLIMS cargado correctamente, cerrando sesión")
    driver.get(mylims_url+"Default/SignOut")

    try:
      WebDriverWait(driver, 10).until(EC.url_contains(labsoft_url))
    except TimeoutException:
      print(f"Error al cerrar sesión, url de login no coincide con {labsoft_url}\nURL ACTUAL: {driver.current_url}\nCerrando...")
      driver.quit()
      input("Presione enter para cerrar")
      exit(1)

    driver.quit()
    input("Presione enter para cerrar")
    exit(0)

except SystemExit:
    exit(0)

except BaseException as e:
    print(f"Error de ejecucion: {e}")
    traceback.print_exc()
    input("Enter para cerrar...")