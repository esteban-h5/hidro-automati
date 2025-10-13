@echo off
:: set "url=https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10021/gs10021w64.exe"
set "url=https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10051/gs10051w64.exe
set "installer=gs10051w64.exe"

echo Descargando y corriendo el instalador desde %url%
echo:

pause
echo:

curl -L -o %installer% %url%
if %errorlevel% neq 0 (
    echo Error al descargar el instalador.
    pause
    exit /b 1
)
echo:

start /wait %installer%

echo Borrando instalador de Ghostscript.
echo:

del %installer%

echo Ghostscript se ha instalado correctamente.
pause