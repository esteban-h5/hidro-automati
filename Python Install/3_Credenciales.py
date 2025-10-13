try:
    from cryptography.fernet import Fernet
    from datetime import datetime
    from getpass import getpass
    from time import sleep
    import keyring, os
    
except ModuleNotFoundError as e:
    input(f"Modulos no instalados: {e}\nEnter para cerrar")
    exit(1)
    
internal_lib =  os.path.dirname(os.path.realpath(__file__))+"\\..\\internal_lib"
param_path = internal_lib+"\\Param.env"
param_exist = os.path.exists(param_path)
token = keyring.get_password('mylims_app', 'secret4')

if os.getenv("mylims_key") != None:
    print("ADVERTENCIA: llave de desencriptación previa guardada en variable de entorno\n")
    os.environ.pop("mylims_key", None)
    
if token != None:
    print("ADVERTENCIA: llave de desencriptación web guardada en sistema\n")

x = ""
if param_exist and token != None:
    x = str(input("Ya existen credenciales registradas, sobrescribir? (S/n): "))

if x != "n":
    user = str(input("Creando archivos de credenciales, escriba a continuacion:\n\nUsuario de labsoft: "))
    passwd = getpass(prompt="Contraseña (Oculta): ")

    if param_exist:
        os.remove(param_path)
        print("Param.env borrado")

    llave = Fernet.generate_key()

    #os.system(f"setx mylims_key {llave.decode()}")
    keyring.set_password("mylims_app", "secret4", llave.decode())

    encuser = Fernet(llave).encrypt(user.encode())
    encpasswd = Fernet(llave).encrypt(passwd.encode())

    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")

    with open(param_path,"w") as archivo:
        archivo.write(f'#Archivo creado en la sesion de {os.getlogin().replace("ñ","$n")} con fecha de {fecha} a las {hora}\nUSER={encuser.decode()}\nPASSWD={encpasswd.decode()}')
        archivo.close()

    print("\nContraseñas encriptadas y archivo de credenciales creado\n")
    input("Enter para cerrar...")
    exit(0)

exit(0)