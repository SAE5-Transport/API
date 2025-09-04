'''
    Friend ENDPOINT
'''
from apifairy import response, other_responses, arguments, body
from flask import Blueprint, request, jsonify
from flask_marshmallow import Marshmallow
from api.services.addFriend import add_friend, get_friends, delete_friend

friend_bp = Blueprint("friend", __name__, url_prefix='/friend')

ma = Marshmallow(friend_bp)


class FriendMessageSuccess(ma.Schema):
    message = ma.String()


class AddFriend(ma.Schema):
    idUser = ma.Int(description="Id of the user")
    idFriend = ma.Int(description="Id of the friend to add")


@friend_bp.route('/add', strict_slashes=False, methods=['POST'])
@body(AddFriend)
@response(FriendMessageSuccess, 201)
@other_responses({400: 'User not found', 500: 'Internal Error'})
def addFriend(data):
    '''
        Add a new friend
    '''
    try:
        data = request.get_json()
        if not data or "idUser" not in data or "idFriend" not in data:
            return jsonify({"error": "Missing user or friend"}), 400

        user = data["idUser"]
        friend = data["idFriend"]

        if user == friend:
            return jsonify({"error": "You cannot add yourself as a friend"}), 400

        add_friend(user, friend)
        return jsonify({"message": f"Friend {friend} added successfully for user {user}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


class Friend_UserId(ma.Schema):
    idUser = ma.Int(description="Id of the user")


class FriendId(ma.Schema):
    friendId = ma.Int(description="Id of the friend")


class ListFriends(ma.Schema):
    friends = ma.List(ma.Nested(FriendId))


@friend_bp.route('/list', strict_slashes=False, methods=['GET'])
@arguments(Friend_UserId)
@other_responses({400: 'Missing user parameter', 500: 'Internal Error'})
def getFriends(data):
    '''
        Get all friends of a user
    '''
    try:
        user = request.args.get("idUser")
        if not user:
            return jsonify({"error": "Missing user parameter"}), 400

        friends = get_friends(user)
        # Ajout de debug
        print(f"DEBUG: Friends found for {user} -> {friends}")

        return jsonify(friends=friends), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@friend_bp.route('/delete', strict_slashes=False, methods=['POST'])
def deleteFriend():
    '''
        Delete a friend
    '''
    try:
        data = request.get_json()
        if not data or "idUser" not in data or "idFriend" not in data:
            return jsonify({"error": "Missing user or friend"}), 400

        user = data["idUser"]
        friend = data["idFriend"]

        delete_friend(user, friend)
        return jsonify({"message": f"Friend {friend} removed successfully for user {user}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
