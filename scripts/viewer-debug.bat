@echo off


ECHO Launching viewer...
SET PATH=%~dp0\..\;%~dp0\..\python\;%PATH%
SET PYTHONPATH=%~dp0\..\
python.exe inode-viewer
