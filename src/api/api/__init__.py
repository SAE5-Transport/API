'''
    Flask API
'''
from flask import Flask
from apifairy import APIFairy

HOST = "localhost"
PORT = 5000

apifairy = APIFairy()

def create_app():
    from api.api.v1 import v1_bp

    app = Flask(__name__)  # Use __name__ instead of "API"
    app.register_blueprint(v1_bp)

    app.config['APIFAIRY_TITLE'] = 'HexaTransit API'
    app.config['APIFAIRY_VERSION'] = '1.0'
    app.config['APIFAIRY_UI'] = "swagger_ui"
    app.config['APIFAIRY_UI_PATH'] = "/"
    apifairy.init_app(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=HOST, port=PORT)