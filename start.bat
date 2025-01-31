if exist .venv rd /s /q .venv
python -m venv .venv
call .venv\Scripts\activate
.venv\Scripts\pip install --upgrade build
python -m build --wheel
for %%f in ("%~dp0dist\*.whl") do (
    pip install "%%f"
)
set FLASK_APP=api
flask run