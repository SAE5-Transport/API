python -m build --wheel
for %%f in ("%~dp0dist\*.whl") do (
    pip install --force-reinstall "%%f"
)
flask --app api run