
IF NOT EXIST "%~dp\python" (
    ECHO INSTALL: Download Python 3...
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.4.3/python-3.4.3.amd64.msi', 'python.msi')"
    ECHO INSTALL: Running Python 3 install...
    msiexec /i python.msi ALLUSERS="" TARGETDIR="%~dp0\python"
    IF ERRORLEVEL 1 (
        IF NOT EXIST "%~dp-\python" (
            ECHO FATAL ERROR: it appears Python 3 failed to install. Try to install it manually.
            PAUSE
            EXIT /B 1
        )
    )
)

ECHO INSTALL: Launching install script...
