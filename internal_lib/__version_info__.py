###############################

version_actual = "6.0.1"
fecha_version = "lunes 5 de diciembre 2025"

changelog = [
    # "- Opción para actualizar base de datos local de ID de metodos",
    "- Errores en columnas en excel de salida en crear muestras, revisar e interrumpir",
    "- Guardar muestras creadas por particion",
]

###############################

import sys, os
wd = os.path.dirname(os.path.realpath(__file__))
param_wd = os.path.join(wd,"Param.env")

if not os.path.exists(param_wd): 
    info = "No existe Param.env"
else:
    with open(param_wd) as param:
        info = param.readline()
        try:
            usuario = info.split("#Archivo creado en la sesion de ")[1].split(" con fecha de ")[0]
            fecha = info.split(" con fecha de ")[1].replace("\n", "")
            info = f'Param creado por {usuario} con fecha de {fecha}'
        except IndexError:
            info = f"ERROR EN TEXTO DE PARAM"

if __name__ == '__main__':
    changelog = '\n'.join(changelog)
    input(f"VERSION PROGRAMAS AUTOMATIZACIÓN {version_actual}\n\n"+
          f"VERSION PYTHON {sys.version}\n\n{info}\n\n"+
          f"Fecha de versión:\n{fecha_version}\n\n"+
          f"Lista de cambios:\n{changelog}\n\n"+
          f"Enter para cerrar")
    