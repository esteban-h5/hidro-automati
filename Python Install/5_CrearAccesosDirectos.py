import os, sys, time
from win32com.client import Dispatch

wd                  =   os.path.dirname(os.path.realpath(__file__))
automatizacion_dir  =   os.path.normpath(os.path.join(wd,".."))
internal_lib        =   os.path.normpath(os.path.join(automatizacion_dir, "internal_lib"))

pyenv_dir           =   os.path.join(internal_lib, "hidro-env")
pyenv_exe           =   sys.executable

sys.path.insert(0, internal_lib)

if os.path.exists(pyenv_dir):
  x = input("se ha instalado pyenv, ¿desea usarlo en los accesos directos? (S/n): ")
  if x != "n":
    pyenv_exe = os.path.join(internal_lib, "hidro-env", "Scripts", "python.exe")

from __version_info__ import version_actual

def crear_acceso_directo(ruta_archivo, ruta_acceso_directo):
    
    shell = Dispatch('WScript.Shell')
    acceso_directo = shell.CreateShortCut(ruta_acceso_directo)

    acceso_directo.TargetPath = pyenv_exe
    acceso_directo.Arguments = f'"{ruta_archivo}"'

    acceso_directo.WorkingDirectory = os.path.dirname(ruta_archivo)
    acceso_directo.IconLocation = r"%SystemRoot%\System32\imageres.dll,201"
    acceso_directo.save()

programs = ["DescargaMuestras", "RegistrosPendientes", "CambiarLotes", "CopiaEnvases", "CrearMuestras"]

try:
  ejecutables = [
      os.path.join(wd,"..","Descarga Muestras","DescargaMuestras.py"),
      os.path.join(wd,"..","Registros Pendientes","RegistrosPendientes.py"),
      os.path.join(wd,"..","Cambiar Lotes","CambiarLotes.py"),
      os.path.join(wd,"..","Copia Envases","CopiaEnvases.py"),
      os.path.join(wd,"..","Crear Muestras","CrearMuestras.py"),
  ]

  lista_escritorios = [
        os.path.join(os.environ['USERPROFILE'],"Desktop"),
        os.path.join(os.environ['USERPROFILE'],"Escritorio"),
        os.path.join(os.environ['USERPROFILE'],"OneDrive","Desktop"),
        os.path.join(os.environ['USERPROFILE'],"OneDrive","Escritorio"),
    ]
    
  check = sum([1 if os.path.exists(dir) else 0 for dir in lista_escritorios])  
  if check != 1:
      print(f"Se encontraron {check} escritorios en el sistema cuando debería ser solo 1")    

  dir_escritorio = ""
  
  for dir in lista_escritorios:
      if os.path.exists(dir):
        dir_escritorio = dir
        break
  else:
      print("No se ha encontrado escritorio para crear accesos directos...")
    
  lista_escritorio = [f for f in os.listdir(dir_escritorio) if os.path.isfile(os.path.join(dir_escritorio, f))]
  time.sleep(.5)
  for archivo in lista_escritorio:
    if ".lnk" in archivo and ("Automatizacion" in archivo or [":" for _ in programs if _ in archivo]):
      x = str(input(f"Archivo {archivo} existe en escritorio, borrar? (S/n): "))
      if x == "n":
        print("Saltado")
      else:
        os.remove( os.path.join(dir_escritorio, archivo) )
  
  for archivo in ejecutables:

    # ruta_script = f'python.exe {"".join(archivo)}'
    
    ruta_script = os.path.normpath("".join(archivo))

    nombre_acceso_directo = f"{os.path.basename(archivo)} {version_actual}"
    
    ruta_acceso_directo = os.path.join(dir_escritorio, nombre_acceso_directo+".lnk")
    
    if not os.path.exists(ruta_acceso_directo):
      crear_acceso_directo(ruta_script, ruta_acceso_directo)
      print(f"Enlace para {nombre_acceso_directo} creado en el escritorio")

    else:
      print(f"Enlace {nombre_acceso_directo} ya existente")

  nombre_acceso_directo = os.path.basename(automatizacion_dir)
  ruta_acceso_directo = os.path.join(dir, f"{nombre_acceso_directo}.lnk")
  
  if not os.path.exists(ruta_acceso_directo):
    shell = Dispatch('WScript.Shell')
    acceso_directo = shell.CreateShortCut(ruta_acceso_directo)
    acceso_directo.WorkingDirectory = os.path.dirname(automatizacion_dir)
    acceso_directo.TargetPath = automatizacion_dir
    acceso_directo.save()

    print(f"Enlace para {nombre_acceso_directo} creado en el escritorio")
  else: 
    print(f"Enlace {nombre_acceso_directo} ya existente")

  print(f"Creados en {dir}")
  
  input("Entrer para cerrar...")
  
except Exception as e:
  print(e)
  input("Error, enter para salir...")