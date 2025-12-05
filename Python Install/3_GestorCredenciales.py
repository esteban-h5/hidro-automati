#!/usr/bin/env python3
# gestor_param_unico.py
# Uso: python gestor_param_unico.py
# Requiere: cryptography, keyring

from cryptography.fernet import Fernet
from datetime import datetime
from getpass import getpass
import keyring
import os
import re
import sys

# --- Configuración de paths ---
internal_lib = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "internal_lib"))
os.makedirs(internal_lib, exist_ok=True)
PARAM_ACTIVE = os.path.join(internal_lib, "Param.env")
SAVE_PATTERN = re.compile(r"save_Param_(\d+)\.env$")
KEYRING_SERVICE = "mylims_app"
KEYRING_KEY = "secret4"

# --- Helpers para keyring y fernet ---
def get_or_create_key():
    token = keyring.get_password(KEYRING_SERVICE, KEYRING_KEY)
    if token:
        # No imprimir la llave por seguridad
        return token.encode()
    else:
        key = Fernet.generate_key()
        keyring.set_password(KEYRING_SERVICE, KEYRING_KEY, key.decode())
        return key

FERNET_KEY = get_or_create_key()
F = Fernet(FERNET_KEY)

# --- I/O de archivos .env ---
def parse_env_file(path):
    """Lee ETIQUETA, USER, PASSWD (sin descifrar) desde un .env. Devuelve dict o None."""
    if not os.path.exists(path):
        return None
    data = {"ETIQUETA": None, "USER": None, "PASSWD": None}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k in data:
                data[k] = v
    return data

def write_env_file(path, etiqueta, enc_user, enc_passwd):
    fecha = datetime.now().strftime("%d/%m/%Y")
    hora = datetime.now().strftime("%H:%M:%S")
    with open(path, "w", encoding="utf-8") as f:
        header_user = os.getlogin().replace("ñ", "$n") if hasattr(os, "getlogin") else "unknown"
        f.write(f"#Archivo creado en la sesion de {header_user} con fecha de {fecha} a las {hora}\n")
        f.write(f"ETIQUETA={etiqueta}\n")
        f.write(f"USER={enc_user}\n")
        f.write(f"PASSWD={enc_passwd}\n")

# --- Gestión de nombres save_Param_n.env ---
def list_save_files():
    files = []
    for fn in os.listdir(internal_lib):
        m = SAVE_PATTERN.match(fn)
        if m:
            n = int(m.group(1))
            files.append((n, os.path.join(internal_lib, fn)))
    files.sort()
    return files  # list of tuples (n, fullpath)

def next_save_filename():
    n = 1
    while True:
        candidate = os.path.join(internal_lib, f"save_Param_{n}.env")
        if not os.path.exists(candidate):
            return candidate
        n += 1

# --- Listado de perfiles (incluye Param.env si existe) ---
def listar_perfiles():
    perfiles = []
    if os.path.exists(PARAM_ACTIVE):
        info = parse_env_file(PARAM_ACTIVE)
        etiqueta = info.get("ETIQUETA") if info else None
        perfiles.append({"archivo": PARAM_ACTIVE, "display": "Param.env (activo)", "etiqueta": etiqueta})
    for n, path in list_save_files():
        info = parse_env_file(path)
        etiqueta = info.get("ETIQUETA") if info else None
        perfiles.append({"archivo": path, "display": os.path.basename(path), "etiqueta": etiqueta})
    return perfiles

# --- Validación de ETIQUETA única ---
def etiqueta_unica(etiqueta):
    for p in listar_perfiles():
        if p["etiqueta"] == etiqueta:
            return False
    return True

# --- Operaciones principales ---
def crear_perfil(etiqueta, user, passwd):
    # cifrar
    enc_user = F.encrypt(user.encode()).decode()
    enc_passwd = F.encrypt(passwd.encode()).decode()
    if not os.path.exists(PARAM_ACTIVE):
        # primer perfil -> se vuelve activo
        write_env_file(PARAM_ACTIVE, etiqueta, enc_user, enc_passwd)
        print(f"\nPerfil creado y activado como Param.env (ETIQUETA={etiqueta}).")
        return PARAM_ACTIVE
    else:
        # ya existe activo -> guardar como save_Param_n.env
        dest = next_save_filename()
        write_env_file(dest, etiqueta, enc_user, enc_passwd)
        print(f"\nPerfil creado y guardado como {os.path.basename(dest)} (ETIQUETA={etiqueta}).")
        return dest

def borrar_perfil(path):
    # No permitir borrar el activo
    if os.path.abspath(path) == os.path.abspath(PARAM_ACTIVE):
        print("No se puede borrar Param.env activo. Primero cambia a otro perfil.")
        return False
    if os.path.exists(path):
        os.remove(path)
        print(f"{os.path.basename(path)} eliminado.")
        return True
    else:
        print("Archivo no encontrado.")
        return False

def switch_perfil(path_to_activate):
    path_to_activate = os.path.abspath(path_to_activate)
    if not os.path.exists(path_to_activate):
        print("Archivo seleccionado no existe.")
        return False
    if os.path.abspath(path_to_activate) == os.path.abspath(PARAM_ACTIVE):
        print("Ese perfil ya está activo.")
        return True
    # mover Param.env actual a next save name
    if os.path.exists(PARAM_ACTIVE):
        dest = next_save_filename()
        os.replace(PARAM_ACTIVE, dest)
        # ahora mover el seleccionado a Param.env
        os.replace(path_to_activate, PARAM_ACTIVE)
        print(f"Perfil cambiado. Nuevo activo: Param.env (desde {os.path.basename(path_to_activate)}).")
        print(f"Anterior activo guardado como {os.path.basename(dest)}.")
        return True
    else:
        # si no hay Param.env (raro), simplemente renombrar elegido a Param.env
        os.replace(path_to_activate, PARAM_ACTIVE)
        print(f"{os.path.basename(path_to_activate)} renombrado a Param.env y activado.")
        return True

# --- Utilidades de interacción con usuario ---
def elegir_perfil(prompt_text="Elige perfil (número): "):
    perfiles = listar_perfiles()
    if not perfiles:
        print("No hay perfiles disponibles.")
        return None
    
    for p in perfiles:
        if "(activo)" in p["display"]:
            perfiles.remove(p)

    print("\nPerfiles disponibles:")

    for idx, p in enumerate(perfiles, start=1):
        etiqueta = p["etiqueta"] or "(sin ETIQUETA)"
        print(f"  {idx}) {p['display']}  - ETIQUETA={etiqueta}")

    while True:
        try:
            sel = input(f"\n{prompt_text}")
            if sel.strip() == "":
                return None
            i = int(sel)
            if 1 <= i <= len(perfiles):
                return perfiles[i-1]["archivo"]
            else:
                print("Índice fuera de rango.")
        except ValueError:
            print("Ingresa un número válido o Enter para cancelar.")

def agregar_flujo():
    print("\n--- Agregar nuevo perfil ---")
    while True:
        etiqueta = input("ETIQUETA (clave única, sin espacios): ").strip()
        if etiqueta == "":
            print("ETIQUETA vacía. Cancelado.")
            return
        if not etiqueta_unica(etiqueta):
            print("ETIQUETA ya existe. Intenta otra.")
            continue
        break
    user = input("Usuario (texto): ").strip()
    passwd = getpass("Contraseña (oculta): ").strip()
    crear_perfil(etiqueta, user, passwd)

def borrar_flujo():
    print("\n--- Borrar perfil ---")
    target = elegir_perfil("Selecciona el número del perfil a borrar (Enter para cancelar): ")
    if not target:
        print("Cancelado.")
        return
    # Confirmar
    b = input(f"Confirma eliminar {os.path.basename(target)}? (s/N): ").strip().lower()
    if b == "s":
        borrar_perfil(target)
    else:
        print("Cancelado.")

def cambiar_flujo():
    print("\n--- Cambiar perfil (switch) ---")
    target = elegir_perfil("Selecciona el número del perfil a activar (Enter para cancelar): ")
    if not target:
        print("Cancelado.")
        return
    switch_perfil(target)

def mostrar_menu():
    print("\nOpciones:")
    print("  1) Agregar perfil")
    print("  2) Borrar perfil")
    print("  3) Cambiar de usuario (activar perfil)")
    print("  4) Listar perfiles")
    print("  5) Salir")

def listar_flujo():
    perfiles = listar_perfiles()
    if not perfiles:
        print("No hay perfiles creados.")
        return
    print("\nPerfiles:")
    for p in perfiles:
        etiqueta = p["etiqueta"] or "(sin ETIQUETA)"
        activo = "(activo)" if os.path.abspath(p["archivo"]) == os.path.abspath(PARAM_ACTIVE) else ""
        print(f" - {os.path.basename(p['archivo'])} {activo}  ETIQUETA={etiqueta}")



# --- Punto de entrada principal ---
def main():
    print("Iniciando gestor de Param.env (misma llave para todos los perfiles).")
    print("\n=== Gestor de Param.env ===")
    print(f"Directorio de perfiles: {internal_lib}")
    # Si no existe keyring key, get_or_create_key ya la creó.
    # Si ya existe un Param.env, mostrar prompt principal; si no, forzar crear primero perfil
    while True:
        if not os.path.exists(PARAM_ACTIVE):
            print("\nNo existe Param.env activo. Tienes que crear el primer perfil.")
            agregar_flujo()
            continue
        mostrar_menu()
        try:
            opt = input("\nSelecciona opción: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo.")
            sys.exit(0)
        if opt == "1":
            agregar_flujo()
        elif opt == "2":
            borrar_flujo()
        elif opt == "3":
            cambiar_flujo()
        elif opt == "4":
            listar_flujo()
        elif opt == "5" or opt.lower() in ("q", "salir", "exit"):
            print("Saliendo.")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
        raise
