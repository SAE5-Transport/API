'''
    User ENDPOINT
'''
from apifairy import response, other_responses, arguments, body
from flask import Blueprint, request, jsonify
from flask_marshmallow import Marshmallow
from api.services.addUser import add_user, getall_user

user_bp = Blueprint("user", __name__, url_prefix='/user')

ma = Marshmallow(user_bp)


class MessageSucces(ma.Schema):
    message = ma.String()


class Userid(ma.Schema):
    idUser = ma.Int(description="Id of the user")


@user_bp.route('/add', strict_slashes=False, methods=['POST'])
@body(Userid)
@response(MessageSucces, 201)
@other_responses({400: 'User not found', 500: 'Internal Error'})
def addUser(data):
    '''
        add User in database
    '''
    try:
        idUser = data.get("idUser")

        if not idUser:
            return jsonify({"error": "Missing idUser"}), 400

        add_user(idUser)
        return jsonify({"message": f"User {idUser} added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


class Userid(ma.Schema):
    idUser = ma.Int(description="Id of the user")


class ListUsers(ma.Schema):
    users = ma.List(ma.Nested(Userid))


@user_bp.route('/test', strict_slashes=False, methods=['GET'])
@response(ListUsers, 200)
def getAllIdUser():
    '''
        get all user in database
    '''
    return {"users": getall_user()}
