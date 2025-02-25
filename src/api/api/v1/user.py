from flask import Blueprint, request, jsonify
from api.services.addUser import add_user, getall_user

user_bp = Blueprint("user", __name__, url_prefix='/user')


@user_bp.route('/add', strict_slashes=False, methods=['POST'])
def addUser():
    '''
        add User in database
    '''
    try:
        data = request.get_json()  # Récupère les données du body en JSON
        if not data or "idUser" not in data:
            return jsonify({"error": "Missing idUser"}), 400

        idUser = data["idUser"]
        add_user(idUser)
        return jsonify({"message": f"User {idUser} added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/test', strict_slashes=False, methods=['GET'])
def getAllIdUser():
    '''
        get all user in database
    '''
    return getall_user()
