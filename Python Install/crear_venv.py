import venv, os
wd = os.path.dirname(os.path.realpath(__file__))
pyenv_dir = os.path.normpath(os.path.join(wd,"..","internal_lib", "hidro-env"))

if not os.path.exists(pyenv_dir):
    print("Creando entorno virtual hidro-env en", pyenv_dir)

    os.mkdir(pyenv_dir)
    venv.create(pyenv_dir, with_pip=True, clear=True)
    
    pyenv_exe = os.path.join(pyenv_dir,"Scripts", "python.exe")
    requirements_path = os.path.join(wd, "requirements.txt")
    os.chdir(wd)
    os.system(f'"{pyenv_exe}" -m pip install --upgrade pip')
    os.system(f'"{pyenv_exe}" -m pip install -r requirements.txt')

    input("pyenv hidro-env creado")

else:
    input(f"hidro-env ya existe en {pyenv_dir}")
    
