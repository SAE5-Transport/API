'''
    Friend ENDPOINT
'''
from apifairy import response, other_responses, arguments, body
from flask import Blueprint, request, jsonify
from flask_marshmallow import Marshmallow
from api.services.addFriend import add_friend, get_friends

friend_bp = Blueprint("friend", __name__, url_prefix='/friend')

ma = Marshmallow(friend_bp)


class MessageSucces(ma.Schema):
    message = ma.String()


class AddFriend(ma.Schema):
    idUser = ma.Int(description="Id of the user")
    idFriend = ma.Int(description="Id of the friend to add")


@friend_bp.route('/add', strict_slashes=False, methods=['POST'])
@body(AddFriend)
@response(MessageSucces, 201)
@other_responses({400: 'User not found', 500: 'Internal Error'})
def addFriend(data):
    '''
        Add a new friend
    '''
    try:
        user = data.get("idUser")
        friend = data.get("idFriend")
        if not user or not friend:
            return jsonify({"error": "Missing user or friend"}), 400

        add_friend(user, friend)
        return jsonify({"message": f"Friend {friend} added successfully for user {user}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


class Friend_UserId(ma.Schema):
    idUser = ma.Int(description="Id of the user")


class Friendid(ma.Schema):
    FriendId = ma.Int(description="Id of the user")


class ListFriends(ma.Schema):
    friends = ma.List(ma.Nested(Friendid))


@friend_bp.route('/list', strict_slashes=False, methods=['GET'])
@arguments(Friend_UserId)
@response(ListFriends, 200)
@other_responses({400: 'Missing user parameter', 500: 'Internal Error'})
def getFriends(data):
    '''
        Get all friends of a user
    '''
    try:
        user = data.get("idUser")
        if not user:
            return jsonify({"error": "Missing user parameter"}), 400

        friends = get_friends(user)
        return jsonify({"friends": friends}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
