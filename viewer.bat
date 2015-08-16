@echo off
IF NOT EXIST %~dp0\python (
    IF EXIST %~dp0\python.msi (
        DEL python.msi
    )
    ECHO PLEASE WAIT !!!   Downloading Python 3...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.4.3/python-3.4.3.amd64.msi', 'python.msi')"
    ECHO PLEASE WAIT !!!   Running Python 3 install...
    msiexec /i python.msi ALLUSERS="" TARGETDIR="%~dp0\python" /q
    IF ERRORLEVEL 1 (
        IF NOT EXIST %~dp0\python (
            ECHO FATAL ERROR: it appears Python 3 failed to install. Try to install it manually.
            PAUSE
            EXIT /B 1
        )
    )
)

ECHO Launching viewer...
SET PATH=%~dp0\;%~dp0\python\;%PATH%
SET PYTHONPATH=%~dp0\
python.exe inode-viewer
pause
