
REM This script is part of information-node
REM Copyright (C) 2015  Information Node Development Team (see AUTHORS.md)
REM
REM This program is free software: you can redistribute it and/or modify
REM it under the terms of the GNU General Public License as published by
REM the Free Software Foundation, either version 2 of the License, or
REM (at your option) any later version.
REM
REM This program is distributed in the hope that it will be useful,
REM but WITHOUT ANY WARRANTY; without even the implied warranty of
REM MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM GNU General Public License for more details.
REM
REM You should have received a copy of the GNU General Public License
REM along with this program.  If not, see <http://www.gnu.org/licenses/>.

@echo off

REM search for a python 3 installation in the PATH environment:
for %%G in ("%path:;=" "%") do (
    IF EXIST %%G\python3.dll (
        IF EXIST %%G\python.exe (
            REM This looks like a valid install, see if the python responds
            REM and whether it is actually reporting to be python 3.
            for /f "tokens=2" %%i in ('%%G\python.exe -V') do (
                for /f "delims=. tokens=1" %%a in ("%%i") do (
                    IF %%a==3 (
                        REM Yup, found it!
                        SET PYTHON_INSTANCE_PATH=%%G
                    )
                )
            )
        )
    )
)

IF DEFINED PYTHON_INSTANCE_PATH (
    ECHO Found python3 at %PYTHON_INSTANCE_PATH%
) ELSE (
    REM Download and install python 3 since we didn't find an install
    REM (we will put it into the local subfolder "python")
    ECHO Localdr %~dp0
    IF NOT EXIST %~dp0\python (
        IF EXIST %~dp0\python.msi (
            DEL %~dp0\python.msi
        )
        ECHO PLEASE WAIT !!!   Downloading Python 3...
        powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.4.3/python-3.4.3.amd64.msi', 'python.msi')"
        ECHO PLEASE WAIT !!!   Running Python 3 install...
        
        REM run the installer in quiet mode:
        msiexec /i python.msi ALLUSERS="" TARGETDIR="%~dp0\python" /q
        
        REM check if the installer had any issues:
        IF ERRORLEVEL 1 (
            IF NOT EXIST %~dp0\python (
                ECHO FATAL ERROR: it appears Python 3 failed to install. Try to install it manually.
                PAUSE
                EXIT /B 1
            )
        )
    )

    REM delete an existing installer file if there's still one lying around:
    IF EXIST %~dp0\python.msi (
       DEL %~dp0\python.msi
    )
    
    REM set this local install as our chosen python path:
    SET PYTHON_INSTANCE_PATH="%~dp0\python\"
)


ECHO Launching viewer...

REM tell python to import stuff from our local ordner too:
SET PYTHONPATH=%~dp0\

REM set our instance as preferred through %PATH% and launch it:
SET PATH="%PYTHON_INSTANCE_PATH%\;%PATH%"
start "" %PYTHON_INSTANCE_PATH%pythonw.exe inode-viewer

