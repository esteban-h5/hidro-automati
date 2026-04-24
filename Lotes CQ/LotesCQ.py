try: #KeybardInterrupt

  import sys,os

  file_name           =   os.path.basename(__file__)
  DM_wd               =   os.path.dirname(os.path.realpath(__file__))
  internal_lib        =   os.path.normpath(os.path.join(DM_wd,"..","internal_lib"))

  sys.path.insert(0, internal_lib)

  from __myLIMS_modulos__ import (
      version_actual, MensajeInicial, notify, sleep, datetime, GetConfig, prefs, 
      DriverOptions, existe_param_env, Chrome, ExcepcionDeCarga, FormatoExcepcion
  )
  from __myLIMS_wrappers__ import (
      DesactivarAlerta, CambiarAcreditacion
  )
  from __ficheros_modulos__ import (
      ListaMuestraXLSX, FilaAgregarXLSX,
  )
  from __myLIMS_wrappers__ import (
      Logout, Login, FormatoLimiteHoras,
  )
  from __myLIMS_API__ import (
      get_samples_ID,
  )

  TI_wd = ""

  config              =   GetConfig( dirConfig=os.path.join(TI_wd,"config.txt") )
  global_config       =   GetConfig( dirConfig=os.path.join(internal_lib,"global_config.txt") )

  keys_used   = ["ejemplo1", "ejemplo2"]
  keys_used_g = ["myLIMSdomain", "Labsoftdomain", "paisActual", "ActivarLOG", "InicioJornada", "ExtensionJornada", "ListaMensajesRutina", "ListaMensajesHoras", "nombreExcelExcepciones", "TipoMensajeETFA", "api-url"]

  for key in keys_used:
      if key not in config.keys():
          input(f"Valor de config \'{key}\' no encontrado en archivo config, enter para continuar igualmente...")
  for key in keys_used_g:
      if key not in global_config.keys():
          input(f"Valor de config \'{key}\' no encontrado en archivo global_config, enter para continuar igualmente...")

  nombreLOG     = os.path.join(DM_wd, "log", datetime.now().strftime('reporte_%Y_%m_%d-%H_%M'))
  nombreRESUMEN = f"{nombreLOG}_RESUMEN.txt"

  myLIMSdomain  = global_config.get("myLIMSdomain", "")
  Labsoftdomain = global_config.get("Labsoftdomain", "")
  api_url       = global_config.get("api-url", "")

  paisActual = global_config.get("paisActual", "").replace("é","e").replace("ú","u").lower()
  log        = global_config.get("ActivarLOG", True)

  ejemplo1      = config.get("ejemplo1", "")
  ejemplo2      = config.get("ejemplo2", "")

  mainUrl                 =   f"{myLIMSdomain}Main.cshtml#Sample/Finalized/List"

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

  MensajeInicial(file_name, funcion_print=eprint, config=config, global_config=global_config, funcion_log=logprint )

  try:
      pais = {
          "chile":            "SCL",
          "peru":             "LIM",
          "colombia":         "BOG",
          "mexico":           "MTY",
      }[paisActual]

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

      metodo = 'Sandbox-RP-Heterótrofos'
      analisis = ''


  except Exception as e:
      notify(title="Problemas en programa", body=type(e).__name__)
      eprint(f"{FormatoExcepcion(e)}\nError al cargar myLIMS")
      input("Enter para cerrar navegador")
      Logout(driver,logout_url=Labsoftdomain)
      driver.quit()
      exit(1)

except KeyboardInterrupt:
    print("Programa interrumpido por el usuario\nProceso del navegador desanclado\nCerrando terminal...")
    from time import sleep
    sleep(1)
    exit(1)