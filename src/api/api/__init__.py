'''
    Flask API
'''
from flask import Flask
from .v1 import v1_bp

app = Flask("API")
app.register_blueprint(v1_bp)

if __name__ == "__main__":
    app.run(debug=True)
