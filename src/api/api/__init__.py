'''
    Flask API
'''
from flask import Flask
from apifairy import APIFairy
from api.api.v1 import v1_bp
from api.utils.config import app_host, app_port

apifairy = APIFairy()

@apifairy.process_apispec
def process_apispec(apispec):
    '''
        Process apispec
    '''

    # Add servers
    apispec['servers'].append({
        'url': f'http://api.hexatransit.clarifygdps.com/',
        'description': 'Production server'
    })
    
    return apispec

def create_app():
    '''
        INIT FLASK APP
    '''

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
    app.run(host=app_host, port=app_port)
