@echo off

set "url=https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe"
set "installer=python-3.13.7-amd64.exe"

set PYTHON_INSTALL=%LOCALAPPDATA%\Programs\Python\Python311
set PYTHON_PATH=%PYTHON_INSTALL%\python.exe

echo Descargando y corriendo el instalador desde %url%
echo:

if not exist "%installer%" (
    powershell -Command "& { (New-Object Net.WebClient).DownloadFile('%url%', '%installer%') }"
) else (
    echo El archivo %installer% ya existe. Se omite la descarga.
    echo:
)

if not exist "%installer%" (
	echo Error al descargar el instalador.
	echo:
	pause
	exit /b 1
)

echo Iniciando instalador de python. (Sin elevar Privilegios)
echo:

python --version >NUL 2>&1
set resultado=%errorlevel%

if %resultado% neq 0 (
	start /wait %installer% /passive InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=0 TargetDir="%PYTHON_INSTALL%"
	
	:: Crear ProgID de usuario
	reg add "HKCU\Software\Classes\Python.File" /ve /d "Python Script" /f >nul 2>&1
	reg add "HKCU\Software\Classes\Python.File\shell\open\command" /ve /d "\"%PYTHON_PATH%\" \"%%1\" %%*" /f >nul 2>&1

	:: Asociar .py a ese ProgID
	reg add "HKCU\Software\Classes\.py" /ve /d "Python.File" /f >nul 2>&1

	echo Asociacion de .py completada.

) else (
	echo Python ya instalado, corriendo sin flags
	start /wait %installer%
)


del %installer%

echo Instalador borrado, programa terminado.
echo:
pause