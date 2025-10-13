from tkinter.filedialog import askdirectory
import os, subprocess, psutil, subprocess
from time import sleep as wait
from tkinter import ttk, Tk
from PyPDF2 import PdfReader, PdfWriter

tipo_archivo = ".pdf"

try:
    wd = os.path.dirname(os.path.realpath(__file__))
    
    impresoras = [_[0] for _ in [__.split("  ") for __ in subprocess.run(["powershell", "-Command", "printer"], capture_output=True, shell=True).stdout.decode("utf-8").split("\n")]]
    [impresoras.pop(0),impresoras.pop(0),impresoras.pop(0),impresoras.pop(len(impresoras)-1),impresoras.pop(len(impresoras)-1),impresoras.pop(len(impresoras)-1)]

    if impresoras[0] == '----': impresoras.pop(0)    
    print("Elegir dispositivo para imprimir\n")
    print(impresoras)
    
    ventana = Tk()
    ventana.geometry("500x275")
    ventana.title("Elegir impresora")

    menu = {}

    for i in range(0,len(impresoras)):
        menu[impresoras[i]] = i+1

    seleccion = ""
    for option in menu:
        def click(option=option, ventana=ventana):
            global seleccion
            seleccion = option
            ventana.destroy()
        ttk.Button(ventana, text=option, command=click, width=50).place(x=100,y=27*menu[option])
    ventana.mainloop()

    if seleccion == "": raise Exception("No se ha seleccionado impresora")

    print(f"Seleccionar directorio con {tipo_archivo}\n")
    directorio = askdirectory(title='Seleccionar carpeta').replace("/","\\")+"\\"
    
    if directorio == "\\": raise Exception("No se ha seleccionado directorio")

    print(f"\nAbriendo:\n{directorio}")
    ListaArchivos = [_ for _ in os.listdir(directorio) if tipo_archivo in _]
    restante = len(ListaArchivos)

    if restante == 0:
        input("No existen archivos pdf en el directorio, enter para salir")
        exit(1)

    [print(f"=>{_}") for _ in ListaArchivos]
    input(f"\nSe imprimirán {restante} archivos pdf en {seleccion}, enter para comenzar")

    os.putenv('COMSPEC',f'C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe')
    indice = 1

    for archivo in ListaArchivos:
        print(f"Restante: {indice}/{restante}\nActual: {archivo}\n")

        archivo_entrada = os.path.join(directorio,archivo)

        reader = PdfReader(archivo_entrada)
        num_paginas = len(reader.pages)

        if num_paginas > 3:
            print(f"PDF con {num_paginas} páginas, cortando a 3 páginas")
            archivo_entrada = os.path.join(directorio,archivo.replace(".pdf","_cortado.pdf"))

            writer = PdfWriter()
            for i in range(3): writer.add_page(reader.pages[i])

            with open(archivo_entrada, "wb") as f_out:
                writer.write(f_out)

        #dejar de preguntar por impresora
        args = ["gswin64c.exe",
                "-sDEVICE=mswinpr2",
                f"-sOutputFile=\"%printer%{seleccion}\"",
                "-sPAPERSIZE=a4",   
                "-dSAFER -dBATCH -dNoCancel -dNOPAUSE -dQUIET", 
                f"\"{archivo_entrada}\""]

        command = " ".join(args)
        print(f"==> {command}")
        while psutil.win_service_get("Spooler").status() != 'running':
            print("ERROR: Servicio \"Cola de Impresión\" (Spooler) no responde...\nFavor reiniciarlo desde Servicios de windows")
            wait(3); subprocess.call("C:\Windows\system32\services.msc", shell=True)
            input("Presione enter cuando el servicio esté corriendo")

        subprocess.call(command, shell=True)
        indice += 1
        if "_cortado" in archivo_entrada:
            print(f"Eliminando copia cortada de {archivo}")
            #os.remove(archivo_entrada)
        
    input("Programa Terminado, enter para cerrar")
    
except KeyboardInterrupt:
    input("Programa cancelado, enter para cerrar")
except Exception as e:
    input(f"{e}, enter para cerrar")