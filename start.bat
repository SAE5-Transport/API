python -m build --wheel
pip install --force-reinstall dist/*
flask --app api run