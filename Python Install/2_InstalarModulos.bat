@echo off

set "url=https://pypi.org/simple/"
setlocal ENABLEEXTENSIONS

:: Revisar la versión de python, en caso de error indicar que no está instalado
python --version 2>NUL
if %errorlevel% neq 0 (
	echo No se encontro Interprete de Python, favor correr 1_InstalarPython.bat
	echo:
	pause
	exit /b 1
)
echo:

:: Revisar python dentro de PATH
where python > nul 2>&1
if %errorlevel% neq 0 (
	echo Python no se encuentra en la variable PATH. Favor de reinstalar con la opcion ^"Add python.exe to PATH^" activa.
	echo:
	pause
	exit /b 1
)

:: Revisar si ya existe la asociación .py
reg query "HKCU\Software\Classes\.py" /ve >nul 2>&1
if %errorlevel% neq 0 (
	echo Python no se ecnuentra asociado a la extension .py.
	echo Favor de cambiarlo en Ajustes del sistema:
	echo Configuración -> Aplicaciones predeterminadas -> Asociar .py con python.exe
	echo:
	pause
	exit /b 1
)

:CONTINUAR
powershell -NoLogo -NoProfile -Command "try { $r = Invoke-WebRequest -Uri $env:url -Method Head -UseBasicParsing -TimeoutSec 10; if ($r.StatusCode -lt 400) { exit 0 } else { exit 1 } } catch { exit 1 }"

if errorlevel 1 (
    echo Error de internet al intentar obtener la web de los modulos
    echo:
    pause
    exit /b 1
)

echo Revisando modulos de Python
echo:

python -m pip install --upgrade pip
:: pip install --upgrade pandas[all]
pip install --upgrade -r requirements.txt 
echo:

echo Se han instalado los modulos correctamente
echo:
pause