'''
    Trajet ENDPOINT
'''
import json
from bson import json_util
from apifairy import response, other_responses, arguments, body
from flask import Blueprint, request, jsonify
from flask_marshmallow import Marshmallow
from api.services.mongo import save, save_json, get_all, get_one, delete

trajet_bp = Blueprint("trajet", __name__, url_prefix='/trajet')

ma = Marshmallow(trajet_bp)


class TrajetMessageSuccess(ma.Schema):
    message = ma.String()


class TrajetData(ma.Schema):
    data = ma.Dict()


@trajet_bp.route('/add', strict_slashes=False, methods=['POST'])
@body(TrajetData)
@response(TrajetMessageSuccess, 201)
@other_responses({400: 'Invalid data', 500: 'Internal Error'})
def add(data):
    '''
        add Trajet
    '''
    try:
        data = data.get("data")

        if not data:
            return jsonify({"error": "Missing data"}), 400

        save(data, "trajet")
        return jsonify({"message": "Trajet add successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
class TrajetList(ma.Schema):
    trajets = ma.Dict()
    
@trajet_bp.route('/getall', strict_slashes=False, methods=['GET'])
@response(TrajetList, 200)
@other_responses({500: 'Internal Error'})
def getAllData():
    '''
        Get all trajets
    '''
    try:
        data = json.loads(json_util.dumps(get_all("trajet")))
        data = {index: value for index, value in enumerate(data)}
        return {"trajets": data}

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


class MongoFilter(ma.Schema):
    filter = ma.Dict()


@trajet_bp.route('/get/<id>', strict_slashes=False, methods=['GET'])
@response(TrajetData, 200)
@other_responses({500: 'Internal Error'})
def getOneData(id):
    '''
        Get a trajet
    '''
    try:
        data = get_one("trajet", {"_id": id})
        return {"data": data}

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@trajet_bp.route('/delete/<id>', strict_slashes=False, methods=['DELETE'])
@response(TrajetMessageSuccess, 200)
@other_responses({500: 'Internal Error'})
def delete(id):
    '''
        Delete a trajet
    '''
    try:
        delete_from_mongo("trajet", {"_id": id})
        return jsonify({"message": "trajet deleted successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
