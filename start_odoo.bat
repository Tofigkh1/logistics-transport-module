@echo off
echo Starting Odoo Server...
cd /d C:\Users\BEST16\Desktop\logistics-transport-module
call venv\Scripts\activate.bat
cd odoo
python odoo-bin -c ..\odoo.conf
pause
