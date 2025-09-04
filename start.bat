if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
    call .venv\Scripts\deactivate
)
timeout /t 2 /nobreak > nul
if exist .venv (
    taskkill /f /im python.exe > nul 2>&1
    timeout /t 2 /nobreak > nul
    rd /s /q .venv
)
timeout /t 2 /nobreak > nul
python -m venv .venv
call .venv\Scripts\activate
.venv\Scripts\pip install --upgrade build
python -m build --wheel
for %%f in ("%~dp0dist\*.whl") do (
    pip install --force-reinstall "%%f"
)
set FLASK_APP=api
flask run