try:
    # import warnings
    # warnings.filterwarnings("ignore", category=DeprecationWarning) 

    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import *
    from selenium.webdriver import Chrome

    from cryptography.fernet import InvalidToken, Fernet
    from datetime import datetime, timedelta, time
    from decouple import Config, RepositoryEnv
    from collections import defaultdict
    from random import randint, choice, uniform
    from time import sleep as wait
    from time import time as tiempo
    from win11toast import notify
    from pathlib import Path

    import os, requests, sys, traceback, subprocess, re, ctypes, keyring, pandas as pd
    from __version_info__ import version_actual

except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)

#Opciones del navegador
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

#Excepciones para interrupción
class ExcepcionDeMuestra(Exception):
    pass

class ExcepcionDeCarga(Exception):
    pass

class ExcepcionArchivo(Exception):
    pass

class ExcepcionDeCodigo(Exception):
    pass

def existe_param_env(path_internal):
  file = os.path.join(path_internal,"Param.env")
  return os.path.exists(file)

#Devolver diccionario con variables del código
def GetConfig(dirConfig):
    
    with open(dirConfig,"r", encoding="utf-8") as configTXT:
        lineas = [_.split(":") for _ in configTXT.read().split("\n") if "#" not in _ and _ != ""]
        configDict = {}

        for items in lineas:
            
            llave = items[0].replace(" ","").replace("\t","")
            valor = re.sub(r'^[ \t]+', '', ":".join(items[1:]))
            
            try:
                configDict[llave] = int(valor)
            except ValueError:
                configDict[llave] = valor

            if str(valor).lower() in ("true", "verdadero"):
                configDict[llave] = True

            if str(valor).lower() in ("false", "falso"):
                configDict[llave] = False

    return configDict


#Devuelve texto para cuando se atrapa una excepción
def FormatoExcepcion(e):
    return f'{traceback.format_exc()}__________________\nExcepción:\t{sys.exc_info()[0]}\nMensaje:\t{e}\nInfo:\t\t{e.__traceback__}\n__________________\n'

def ExtraerTabla(driver,XPATH):
    tabla = driver.find_element(By.XPATH, XPATH)

    e_columnas = tabla.find_element(By.CLASS_NAME, "k-grid-header").find_elements(By.TAG_NAME, "th")
    colnames = [celda.get_attribute("textContent") for celda in e_columnas]
    
    filas = tabla.find_element(By.CLASS_NAME, "k-grid-content").find_elements(By.TAG_NAME, "tr")
    datos = [[celda.get_attribute("textContent") for celda in fila.find_elements(By.TAG_NAME, "td")] for fila in filas]

    return [colnames, datos]

#Obtener atrubuto style de barra naranja y esperar que contenga block para indicar que se encuentra activo
def queue_redy(driver):
    try:
        queue_style = driver.find_element(By.XPATH ,'//*[@id="queue_notice"]').get_attribute("style")
    except NoSuchElementException:
        return False
        
    if 'display' not in queue_style:
        return False
    else:
        return 'none' in [_ for _ in queue_style.split(";") if 'display' in _][0]


def alerta_visible(driver):
    for element in driver.find_elements(By.XPATH,'//*[@data-role="draggable"]'):
        style = element.get_attribute("style")
        if "visibility: visible;" in style and "display: block;" in style:
            return True
    else:
        return False


def obtener_version_chrome():
    try:
        req_key = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
        output = subprocess.check_output(req_key, shell=True).decode()
        version = output.split()[-1]
        return version
    except Exception:
        return "ERROR al obtener versión"

def MensajeInicial(filename, login_url, init_url, funcion_print=print,):

    funcion_print(f'-------------------------\n'+
                  f'Programa {filename} - Versión: {version_actual} - venv: {sys.prefix != sys.base_prefix}\n'+
                  f'Versión Python: {sys.version}\n'+
                  f'Versión actual de chrome: {obtener_version_chrome()}\n'+
                  f"Fecha Actual: {datetime.now().strftime('%a %d/%m %H:%M:%S')}\n"+
                #   f"Fecha Actual: {datetime.now().strftime('%a %-d de %B %H:%M:%S')}\n"+
                #   f'Dirección Objetivo para myLIMS: {init_url}\n'+
                  f'-------------------------\n')
    wait(3)

def AlternarMedidaVentana(driver):
    if driver.get_window_size()["width"] == 1199:
        driver.set_window_size(1200,710) 
    else: 
        driver.set_window_size(1199,709)

def del_alertas_iniciales(driver, xalerta, xboton):
    try:
        alerta = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, xalerta)))
        if "iframe" in alerta:
            driver.switch_to.frame(alerta)
            alerta.find_element(By.XPATH, xboton).click()
            driver.switch_to.default_content()
        else:
            alerta.find_element(By.XPATH, xboton).click()

    except TimeoutException:
        pass

    return False

def EsperarCARGA_myLIMS(driver, reintentos=60, kill=True, funcion_print=print, recargar=True, resize=True, extra=None, espera=0, revisar_overlay=True):
    wait(espera)
    mover_mouse_antiSalvapantallas()

    for _ in range(5):    
        if revisar_overlay:
            try:
                overlay = WebDriverWait(driver, .5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="k-overlay"]')))
                driver.execute_script("arguments[0].remove();", overlay)
                
            except (TimeoutException, StaleElementReferenceException):
                pass
                

        if resize: AlternarMedidaVentana(driver)
        for _ in range(reintentos):
            wait(1)
            try:
                if 'pace-inactive' in driver.execute_script('return document.querySelector("body > div.pace").getAttribute("class");'):
                    if extra == None:
                        return 0
                    else:
                        wait(extra)
                        return 0
                
            except JavascriptException:
                pass
        
        if recargar: 
            funcion_print("Elevado tiempo de espera, recargando mylims")
            driver.refresh()
        wait(5)

    if kill: raise ExcepcionDeCarga(f'Timeout al esperar carga de myLIMS')
    else:
        funcion_print("Timeout al esperar carga de myLIMS")
        return 1

def ChequearNavegador(driver, kill=False):
    try:
        driver.get_window_position()
    except NoSuchWindowException:
        if kill: raise ExcepcionDeMuestra("No se ha encontrado ventana del navegador")
        input("No se ha encontrado ventana del navegador, enter para continuar")
    else:
        if "signout=true" in driver.current_url:
            if kill: raise ExcepcionDeMuestra("Se ha cerrado las sesion manualmente")
            input("Se ha cerrado las sesion manualmente")

def SiExisteElemento(driver,atributo,valor,XPATH=None):
    if XPATH == None:
        Xpath = '//*[@'+str(atributo)+'="'+str(valor)+'"]'
    else:
        Xpath = XPATH

    try: 
        driver.find_element(By.XPATH, Xpath)
    except NoSuchElementException:
        return False
    else:
        return True

def EsperarCLICK(driver, elemento=None, valor=None, atributo=None, timeout=120, kill=False, funcion_print=print):
    if elemento != None and atributo == None and valor == None:
        try:
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(elemento) ).click()
            return 1
        except TimeoutException:
            if kill: 
                raise ExcepcionDeMuestra(f'Timeout al esperar click de {valor}')
            else: 
                funcion_print(f'Timeout al esperar click de {valor}, continuando igualmente')
            return 0


    if atributo != None and valor != None:
        try:
            Xpath = '//*[@'+str(atributo)+'="'+str(valor)+'"]'
            WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH,Xpath))).click()
            return 1
        except TimeoutException:
            if kill: raise ExcepcionDeMuestra(f'Timeout al esperar click de {valor}')
            input(f'no se pudo encontrar {Xpath}, favor de encontrarlo y hacerle click')
            return 0
        
        except ElementClickInterceptedException:
            if kill: raise ExcepcionDeMuestra(f'Timeout al esperar click de {valor}')
            input(f'{Xpath}Encontrado pero no se le puede hacer click, favor de hacerle click para continuar')
            return 0

    if atributo == None and valor == None:
        return 0
    
def EsperarPRECENCIA(driver,atributo,valor,timeout=120,kill=False):
    Xpath = '//*[@'+str(atributo)+'="'+str(valor)+'"]'
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH,Xpath)))
    except TimeoutException:
        if kill: raise ExcepcionDeMuestra(f'Timeout al esperar elemento {valor}')
        input(f'No se encontro {Xpath}, enter para continuar')

def EsperarVentana(driver,segundos=3):
    Xpath = f'//div[@class="k-widget k-window" and contains(@style, "display: block")]'
    try:
        WebDriverWait(driver, segundos).until(EC.presence_of_element_located((By.XPATH,Xpath)))
        #Ventana Encontrada
        return True
    except TimeoutException:
        #No hay Ventana
        return False
    
def BotonAccion(driver, data_test, log=False, funcion_print=print): #Volver, Editar, Alterar
    if log: funcion_print(f"click boton accion {data_test}")
    return driver.find_element(By.XPATH, f'//div[@id="InterfaceActions"]//div[@class="labsoft-ui-buttons-bar" and not(@style="display: none;")]//button[@data-test="{data_test}"]')

def BotonSection(driver, data_test, log=False, funcion_print=print): #Detalles, Muestra, Historial, Mensajes
    if log: funcion_print(f"click boton section {data_test}")
    return driver.find_element(By.XPATH, f'//div[@id="InterfaceSections"]//div[@data-test="{data_test}"]')

def BotonVentana(driver, data_test, log=False, funcion_print=print): #Ventana PopUp
    if log: funcion_print(f"click boton ventana {data_test}")
    return driver.find_element(By.XPATH, f'//div[@class="k-widget k-window" and contains(@style, "display: block")]//button[@data-test="{data_test}"]')

def EsperarDESAPARECER(driver,atributo,valor,timeout=120,kill=False):
    Xpath = '//*[@'+str(atributo)+'="'+str(valor)+'"]'
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, Xpath)))
    except TimeoutException:
        if kill: raise ExcepcionDeMuestra(f'Timeout, no se pudo encontrar {valor} para esperar que desaparezca')
        input(f'No se encontro {Xpath}, favor de revistar navegador enter para continuar')

    finally:
        try:
            WebDriverWait(driver, timeout).until(EC.none_of( EC.presence_of_element_located((By.XPATH, Xpath)) ))
        except TimeoutException:
            if kill: raise ExcepcionDeMuestra(f'Timeout al esperar desaparecer elemento {valor}')
            input(f'TIMEOUT aún no desaparece {Xpath}\nse interrumpio por si acaso')

def BuscarTEXTO(driver,atributo,valor,timeout=120,kill=False):
    Xpath = '//*[@'+str(atributo)+'="'+str(valor)+'"]'
    try:
        texto = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, Xpath)))
        return texto.text
    except TimeoutException:
        if kill: raise ExcepcionDeMuestra(f'Timout, no se pudo encontrar el texto en {valor}')
        input(f'No se pudo encontrar texto con xpath: {Xpath}')
        return ""

####################################
# MOVER MOUSE para no saltar salvapantallas
####################################

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class INPUT(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("mi", MOUSEINPUT)]

def mover_mouse_antiSalvapantallas():
    extra = ctypes.c_ulong(0)
    ii_ = INPUT()
    ii_.type = 0 

    # Lista de movimientos en las cuatro direcciones
    direcciones = [(1, 0), (0, 1), (-1, 0), (0, -1)] 

    for dx, dy in direcciones:
        ii_.mi.dx = dx
        ii_.mi.dy = dy
        ii_.mi.mouseData = 0
        ii_.mi.dwFlags = 0x0001  # MOUSEEVENTF_MOVE
        ii_.mi.time = 0
        ii_.mi.dwExtraInfo = ctypes.pointer(extra)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(ii_), ctypes.sizeof(ii_))
        wait(0.05)  # Pausa breve entre movimientos
